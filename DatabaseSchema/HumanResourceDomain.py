# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call

from .HumanResourceSchema import *

HumanResourceDomain = {
    'schema': HumanResourceSchema,
    'item_title': 'Human in factory',
    'resource_title':'factory/{factoryId}/human',
    # collection to store data
    'datasource': {
        'source': 'resource'
    },
    # which API call allow to access human data
    'url': 'factory/<regex("[a-f0-9]{24}"):factoryInfo>/<regex("human"):resourceType>'
}