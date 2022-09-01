# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call

from .TransformSchema import *
from .Transform2DSchema import *
from .PlanSchema import PlanSchema
from .Volume import Volume

ElementSchema = {
    'name':
    {
        'type': 'string',
        'required': True,
    },
    'factoryInfo':
    {
        'type': 'objectid',
        'required': True,
        # referential integrity constraint: value must exist in the 'factory' collection. Since we aren't declaring a 'field' key,
        # will default to `factory._id` (or, more precisely, to whatever ID_FIELD value is).
        'data_relation':
        {
            # specify the DOMAIN name to access for checking
            'resource': 'factory',
            # make the factoryInfo embeddable with ?embedded={"factoryInfo":1}
            'embeddable': True
        }
    },
    'transform': 
    {
        'type': 'dict',
        'required': False,
        'schema': TransformSchema
    }, 
    'transform2D': 
    {
        'type': 'dict',
        'required': False,
        'nullable': True,
        'schema':Transform2DSchema
    },
    'stockInfo':
    {
        'type': 'objectid',
        'required': False,
        'data_relation':
        {
        #     # specify the DOMAIN name to access for checking
            'resource': 'stock',
        #     # make the resourceInfo embeddable with ?embedded={"operationInfoList":1}
            'embeddable': True
        },
    },
    'plan':
    {
        'type': 'dict',
        'required': False,
        'schema': PlanSchema,
    },
    'volume':
    {
        'type': 'dict',
        'required': False,
        'schema': Volume,
    },
}
