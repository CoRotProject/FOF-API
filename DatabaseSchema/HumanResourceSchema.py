# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call

from .ResourceSchema import *

HumanResourceSchema = dict(ResourceSchema)
HumanResourceSchema.update({
    'resourceType': # override from FactoryResourceSchema
    {
        'type': 'string',
        'allowed':['human'],   # TO KEEP ADDING AS YOU ADD A PARTICULAR RESOURCE...
        'required': True,
        'default': 'human'
    },
    'role': 
    {
        'type': 'string',
        'allowed':['engineer', 'operator'],
        'required': True
    }
})