# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .ProductSchema import *

ProductDomain = {
    'schema': ProductSchema,
    'item_title': 'Product in factory',
    'resource_title':'factory/{factoryId}/product',
    # collection to store data
    'datasource': {
        'source': 'product'
    },
    # which API call allow to access product data
    'url': 'factory/<regex("[a-f0-9]{24}"):factoryInfo>/product',
    'mongo_indexes':{
        'factoryInfoIndexAsc':[('factoryInfo', 1)],
        'factoryInfoIndexDesc':[('factoryInfo', -1)]
    }
}