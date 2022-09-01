# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call

from .ElementSchema import *

StockSchema = dict(ElementSchema)
StockSchema.update({
    'mode': {
        'type': 'string',
        'allowed':['init', 'in', 'out', 'mixte', 'internal', 'final'],
        'required': True
    },
    'stockType': {
        'type': 'string',
        'allowed':['stockProduct', 'stockPart','stockMixte'],   
        'required': True,
        'default': 'stockPart'
    },
    'partReferenceStockable': {
        'type': 'string',
        'required': False
    },
    'productInfoList': {
        'type':'list',
        'nullable': True,
        'default': None,
        'required': False,
        'schema': {
            'type': 'objectid',
            'data_relation': {
                # specify the DOMAIN name to access for checking
                'resource': 'product',
                'embeddable': True
            }
        }
    },
    'size': {
        #size de la forme [nb horizontal(x), nb verticale(y), deltax,deltay]
        'type':'dict',
        'default': {'nbx':1, 'nby':1, 'deltax':0.0, 'deltay':0.0},
        'required': True,
        'schema':{
            'nbx':{'type': 'integer', 'default': 1},
            'nby':{'type': 'integer', 'default': 1},
            'deltax':{'type': 'float', 'default': 0},
            'deltay':{'type': 'float', 'default': 0},
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
            'resource': 'resource',
            # make the link embeddable with ?embedded={"link":1}
            'embeddable': True
        }
    },
})