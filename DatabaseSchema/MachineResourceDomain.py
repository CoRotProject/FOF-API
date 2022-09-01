# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call

from .MachineResourceSchema import *

MachineResourceDomain = {
    'schema': MachineResourceSchema,
    'item_title': 'Machine in factory',
    'resource_title':'factory/{factoryId}/machine',
    # collection to store data
    'datasource': {
        'source': 'resource'
    },
    # which API call allow to access robot data
    'url': 'factory/<regex("[a-f0-9]{24}"):factoryInfo>/<regex("machine"):resourceType>'
}