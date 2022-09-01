# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .OperationSchema import *

OperationGrabSchema = dict(OperationSchema)
OperationGrabSchema.update({
    'params':
    {
        'type':'dict',
        'required': True,
        'schema':
        {
            'position': 
            {
                'type': 'dict',
                'required': True,
                'nullable': True,
                'schema':TransformSchema
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
			'parameters':
            {
                'type': 'string',
                'required': False,
            },
			'function':
            {
                'type': 'string',
                'required': False,
                'default': "grab"
            },
        }
    },
    # the type of task. This value will be overridden by Child Task defined
    'operationType':
    {
        'type': 'string',
        'required': True,
        'default':'grab'
    },
    #'params':{} # depends on the type of operation
})