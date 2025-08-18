# hubspot.py
import json
import secrets
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import asyncio
import time


import requests
from integrations.integration_item import IntegrationItem
from integrations.hubspot_endpoint_mapping import HUBSPOT_ENDPOINT_MAPPING

from redis_client import add_key_value_redis, get_value_redis, delete_key_redis


RATE_LIMIT_DELAY = 0.1 # Delay in seconds to avoid hitting rate limits
CLIENT_ID = 'XXX'
CLIENT_SECRET = 'XXXXXX'
REDIRECT_URI = 'http://localhost:8000/integrations/hubspot/oauth2callback'
SCOPES = 'oauth crm.objects.companies.read crm.objects.contacts.read crm.objects.deals.read tickets'
BASE_URL = 'https://api.hubapi.com'

# Fetching only these main objects from Hubspot it can be extended as needed
HUBSPOT_OBJECTS_LIST = ['companies', 'contacts', 'deals', 'tickets'] 


authorization_url = f'https://app.hubspot.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fintegrations%2Fhubspot%2Foauth2callback&scope={SCOPES}'


async def authorize_hubspot(user_id, org_id):
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id
    }
    encoded_state = json.dumps(state_data)
    await add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', encoded_state, expire=600)

    return f'{authorization_url}&state={encoded_state}'

async def oauth2callback_hubspot(request: Request):
    if request.query_params.get('error'):
        raise HTTPException(status_code=400, detail=request.query_params.get('error'))
    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')
    state_data = json.loads(encoded_state)

    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')

    saved_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}')

    if not saved_state or original_state != json.loads(saved_state).get('state'):
        raise HTTPException(status_code=400, detail='State does not match.')

    async with httpx.AsyncClient() as client:
        response, _ = await asyncio.gather(
            client.post(
                'https://api.hubapi.com/oauth/v1/token',
                data = {
                    "grant_type": "authorization_code",
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "redirect_uri": REDIRECT_URI,
                    "code": code
                    }

            ),
            delete_key_redis(f'hubspot_state:{org_id}:{user_id}'),
        )

    await add_key_value_redis(f'hubspot_credentials:{org_id}:{user_id}', json.dumps(response.json()), expire=600)
    
    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    return HTMLResponse(content=close_window_script)

async def get_hubspot_credentials(user_id, org_id):
    credentials = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    credentials = json.loads(credentials)
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    await delete_key_redis(f'hubspot_credentials:{org_id}:{user_id}')

    return credentials

async def create_integration_item_metadata_object(
        response_json: str, item_type: str, url= None) -> IntegrationItem:
    name = None
    if item_type == 'company':
        name = response_json.get('properties', {}).get('name', None)
        if not name:
            name = response_json.get('properties', {}).get('domain', None)
    elif item_type == 'contact':
        first_name = response_json.get('properties', {}).get('firstname', None)
        last_name = response_json.get('properties', {}).get('lastname', None)
        if first_name:
            name = first_name
            if last_name:
                name += f' {last_name}'
        email = response_json.get('properties', {}).get('email', None)
        if name and email:
            name += f' ({email})'
        elif not name and email:
            name = email
    elif item_type == 'deal':
        name = response_json.get('properties', {}).get('dealname', None)
    elif item_type == 'ticket':
        name = response_json.get('properties', {}).get('subject', None)

    integration_item_metadata = IntegrationItem(
        id=response_json.get('id', None),
        name=name,
        type=item_type,
        creation_time= response_json.get('createdAt', None),
        last_modified_time= response_json.get('updatedAt', None),
        url=url+ f'/{response_json.get("id", None)}' if url else None,
    )

    return integration_item_metadata

    
def fetch_items(
    access_token: str, url: str, aggregated_response: list, offset=None, properties=None
) -> dict:
    
    params = {'limit': 10, 'archived': 'false'}
    if properties:
        params['properties'] = properties
    if offset:
        params['after'] = offset
        

    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        results = response.json().get('results', {})
        offset = None
        paging = response.json().get('paging', None)
        if paging and 'next' in paging:
            offset = paging['next'].get('after', None)
 
        aggregated_response.extend(results)
        print(results)

        if offset:
            time.sleep(RATE_LIMIT_DELAY)  # Respect rate limits
            fetch_items(access_token, url, aggregated_response, offset, properties)
        else:
            return
    else:
        print(f'Failed to fetch items from Hubspot: {response.text}')

async def get_items_hubspot(credentials):
    """Aggregates all metadata relevant for a hubspot integration"""
    credentials = json.loads(credentials)

    create_integration_item_metadata_list = []

    for object in HUBSPOT_OBJECTS_LIST:
        if object in HUBSPOT_ENDPOINT_MAPPING:
            aggregated_response = []
            print(f'Fetching {object} items from Hubspot...')

            endpoint = HUBSPOT_ENDPOINT_MAPPING[object]['endpoint']
            url = f'{BASE_URL}{endpoint}'
            fetch_items(access_token=credentials.get('access_token'), 
                        url=url, 
                        aggregated_response=aggregated_response,
                        properties=HUBSPOT_ENDPOINT_MAPPING[object].get('properties', None))
            print(f'Fetched {len(aggregated_response)} items from Hubspot for {object}.')

            for response_json in aggregated_response:
                integration_item_metadata = await create_integration_item_metadata_object(response_json=response_json, 
                                                                                      item_type=HUBSPOT_ENDPOINT_MAPPING[object]['object_type'], url=url)


                create_integration_item_metadata_list.append(integration_item_metadata)
        else:
            print(f'No endpoint mapping found for {object}. Skipping...')

    for item in create_integration_item_metadata_list:
        print(item)

    return