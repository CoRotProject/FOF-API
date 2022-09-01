# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .ElementSchema import *
from .ProductOperationAndStatusSchema import *

ProductSchema = dict(ElementSchema)
ProductSchema.update({
    # reference of the product
    'reference':
    {
        'type': 'string',
        'required': True,
    },
    # list of operation to do ordered
    'operationToDoList': 
    {
        'type': 'list',
        'nullable': True,
        'default': None,
        'required': True,
        'schema':
        {
            'type': 'dict',
            'schema':ProductOperationAndStatusSchema
        }
    },
    'currentOperationInfo':
    {
        'type': 'objectid',
        'nullable': True,
        'default': None,
        'required': True,
        'data_relation':
            {
                # specify the DOMAIN name to access for checking
                'resource': 'operation',
                # make the currentOperationInfo embeddable with ?embedded={"currentOperationInfo":1}
                'embeddable': True
            }
    },
    'link': {
        'type': 'objectid',
        'required': False,
        # physical link between stock and other objet in factory
        # position is defined in function of the linked object
        # referential integrity constraint: value must exist in the 'factory' collection. Since we aren't declaring a 'field' key,
        # will default to `factory._id` (or, more precisely, to whatever ID_FIELD value is).
        'data_relation':
        {
            # specify the DOMAIN name to access for checking
            'resource': 'stock',
            # make the link embeddable with ?embedded={"link":1}
            'embeddable': True
        }
    },
    'produced': 
    { 
        'type': 'boolean', 
        'required': True, 
        'default': False
    }
})