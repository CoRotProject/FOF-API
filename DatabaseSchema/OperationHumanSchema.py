# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .OperationSchema import *

OperationHumanSchema = dict(OperationSchema)
OperationHumanSchema.update({
    'params':
    {
        'type':'dict',
        'required': True,
        'schema':
        {
			'taskstodo':
            {
                'type': 'list',
                'required': True,
                'schema':{
					'type': 'string',
					'required': False,
				}
            },
        }
    },
    'operationType':
    {
        'type': 'string',
        'required': True,
        'default':'humanaction'
    }
    
})