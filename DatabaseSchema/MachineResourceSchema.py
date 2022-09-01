# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .ResourceSchema import *
from .MachineOperationCapabilitySchema import *

MachineResourceSchema = dict(ResourceSchema)
MachineResourceSchema.update({
    'resourceType': # override from FactoryResourceSchema
    {
        'type': 'string',
        'allowed':['machine'],   # TO KEEP ADDING AS YOU ADD A PARTICULAR RESOURCE...
        'required': True,
        'default': 'machine'
    },
    # list of product on it
    'currentProductInfoList':
    {
        'type':'list',
        'nullable': True,
        'default': None,
        'required': True,
        'schema':
        {
            'type': 'objectid',
            'data_relation':
            {
                # specify the DOMAIN name to access for checking
            'resource': 'product',
                'embeddable': True
            }
        }
    }, 
    'resourceCapabilityList':
    {
        'type':'list',
        'nullable': True,
        'default': None,
        'required': True,
        'schema':
        {
            'type': 'dict',
            'nullable':True,
            'schema':MachineOperationCapabilitySchema
        }
    },
    'stockList': #list of stocks case
    {
        'type':'list',
        'nullable': True,
        'default': [],
        'required': True,
        'schema':
        {
            'type': 'objectid',
            'data_relation':
            {
                # specify the DOMAIN name to access for checking
                'resource': 'stock',
                'embeddable': True
            }
        }
    },
    
    'stockProductList':
    {
        'type':'list',
        'nullable': True,
        'default': None,
        'required': True,
        'schema':
        {
            'type': 'objectid',
            'data_relation':
            {
                # specify the DOMAIN name to access for checking
                'resource': 'product',
                'embeddable': True
            }
        }
    },

    'stockPartList':
    {
        'type':'list',
        'nullable': True,
        'default': None,
        'required': True,
        'schema':
        {
            'type': 'objectid',
            'data_relation':
            {
                # specify the DOMAIN name to access for checking
                'resource': 'stockPart',
                'embeddable': True
            }
        }
    },
})