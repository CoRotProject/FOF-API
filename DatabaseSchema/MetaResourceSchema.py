# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call

from .ResourceSchema import *

MetaResourceSchema = dict(ResourceSchema)
MetaResourceSchema.update({
    'resourceType': # override from FactoryResourceSchema
    {
        'type': 'string',
        'allowed':['meta'],   # TO KEEP ADDING AS YOU ADD A PARTICULAR RESOURCE...
        'required': True,
        'default': 'meta'
    },
    'metaType': 
    {
        'type': 'string',
        'allowed':['pickandmove', 'misc'],
        'required': True,
        'default': 'pickandmove'
    },
    'composition':
    {
        'type': 'list',
        'required': True,
        'default':[],
        'schema':
        {
            'type': 'objectid',
            'required': True,
            'data_relation':
            {
                # specify the DOMAIN name to access for checking
                'resource': 'resource',
                # make the resourceInfo embeddable with ?embedded={"operationInfoList":1}
                'embeddable': True
            }
        }       
    },
    'taskList': 
    {
        'type': 'list',
        'required': True,
        'default':[],
        'schema':
        {
            'type': 'objectid',
            'required': True,
            'data_relation':
            {
                # specify the DOMAIN name to access for checking
                'resource': 'task',
                # make the resourceInfo embeddable with ?embedded={"operationInfoList":1}
                'embeddable': True
            }
        }
    },

})