# Mapping of HubSpot objects to their corresponding endpoints



HUBSPOT_ENDPOINT_MAPPING = {
    # CRM Objects
    'carts': {
        'endpoint': '/crm/v3/objects/carts',
        'object_type': 'cart',
        'properties': 'name,createdate,lastmodifieddate,hs_cart_status'
    },
    'contacts': {
        'endpoint': '/crm/v3/objects/contacts',
        'object_type': 'contact',
        'properties': 'createdate,lastmodifieddate,email,firstname,lastname,phone,website,hs_object_id'
    },
    'companies': {
        'endpoint': '/crm/v3/objects/companies',
        'object_type': 'company',
        'properties': 'name,domain,industry,city,state,country,phone,numberofemployees,annualrevenue,createdate,lastmodifieddate'
    },
    'deals': {
        'endpoint': '/crm/v3/objects/deals',
        'object_type': 'deal',
        'properties': 'dealname,amount,dealstage,pipeline,closedate,createdate,lastmodifieddate,dealtype,description'
    },
    'discounts': {
        'endpoint': '/crm/v3/objects/discounts',
        'object_type': 'discount',
        'properties': 'name,amount,createdate,lastmodifieddate'
    },
    'fees': {
        'endpoint': '/crm/v3/objects/fees',
        'object_type': 'fee',
        'properties': 'name,amount,createdate,lastmodifieddate'
    },
    'goals': {
        'endpoint': '/crm/v3/objects/goal_targets',
        'object_type': 'goal',
        'properties': 'name,description,goal_type,createdate,lastmodifieddate'
    },
    'invoices': {
        'endpoint': '/crm/v3/objects/invoices',
        'object_type': 'invoice',
        'properties': 'name,amount,status,createdate,lastmodifieddate,hs_invoice_number'
    },
    'payments': {
        'endpoint': '/crm/v3/objects/payments',
        'object_type': 'payment',
        'properties': 'name,amount,status,createdate,lastmodifieddate,hs_payment_method'
    },
    'quotes': {
        'endpoint': '/crm/v3/objects/quotes',
        'object_type': 'quote',
        'properties': 'name,amount,status,createdate,lastmodifieddate,hs_quote_number'
    },
    
    'products': {
        'endpoint': '/crm/v3/objects/products',
        'object_type': 'product',
        'properties': 'name,description,price,createdate,lastmodifieddate,hs_sku'
    },
    'orders': {
        'endpoint': '/crm/v3/objects/orders',
        'object_type': 'order',
        'properties': 'name,amount,status,createdate,lastmodifieddate,hs_order_number'
    },
    
    # Engagements
    'engagements': {
        'endpoint': '/engagements/v1/engagements/paged',
        'object_type': ['CALL', 'EMAIL', 'MEETING', 'NOTE', 'TASK'],
        'properties': 'hs_activity_type,hs_body_preview,createdate,lastmodifieddate,hubspot_owner_id'
    },
    
    # Service Hub
    'tickets': {
        'endpoint': '/crm/v3/objects/tickets',
        'object_type': 'ticket',
        'properties': 'subject,content,hs_ticket_priority,hs_ticket_status,createdate,lastmodifieddate'
    },
    
    
    
    
}
