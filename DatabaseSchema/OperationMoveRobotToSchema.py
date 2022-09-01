# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .OperationSchema import *

OperationMoveRobotToSchema = dict(OperationSchema)
OperationMoveRobotToSchema.update({
    'params':
    {
        'type':'dict',
        'required': True,
        'schema':
        {
            'transform2D': 
            {
                'type': 'dict',
                'required': True,
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
        },
    },
    'operationType':
    {
        'type': 'string',
        'required': True,
        'default':'robotmove'
    },
    
})