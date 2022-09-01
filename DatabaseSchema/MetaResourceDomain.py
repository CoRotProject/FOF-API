# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call

from .MetaResourceSchema import *

MetaResourceDomain = {
    'schema': MetaResourceSchema,
    'item_title': 'Human in factory',
    'resource_title':'factory/{factoryId}/meta',
    # collection to store data
    'datasource': {
        'source': 'resource'
    },
    # which API call allow to access meta ressource data
    'url': 'factory/<regex("[a-f0-9]{24}"):factoryInfo>/<regex("meta"):resourceType>'
}