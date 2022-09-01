# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .OperationSchema import *

OperationMachineSchema = dict(OperationSchema)
OperationMachineSchema.update({
    'params':
    {
        'type':'dict',
        'required': True,
        'schema':
        {
			'parameters':
            {
                'type': 'string',
                'required': False,
            },
			'function':
            {
                'type': 'string',
                'required': False,
                'default': "produire"
            },
        }
    },
    # the type of task. This value will be overridden by Child Task defined
    'operationType':
    {
        'type': 'string',
        'required': True,
        'default':'production'
    },
})