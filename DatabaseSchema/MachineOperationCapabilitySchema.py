# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call

from .ResourceCapabilitySchema import *

# TODO replace ResourceCapabilitySchema
MachineOperationCapabilitySchema = dict(ResourceCapabilitySchema)
MachineOperationCapabilitySchema.update({
    'category':
    {
        'type': 'string',
        'required':True,
        'allowed': ['transformation', 'transport', 'wait', 'grab', 'production', ]
    },
    'capability':
    {
        'type': 'string',
        'required': False
    },
    'quality':
    {
        'type': 'string',
        'allowed':['low', 'medium', 'high'], 
        'default': 'high',
        'required': True,
    },
    'duration': 
    {
        'type': 'float',
        'default': 10.0,
        'required': True
    },
    'variance': 
    {
        'type': 'float',
        'default': 1.0,
        'required': True
    }    
})