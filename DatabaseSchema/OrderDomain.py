# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .OrderSchema import *

OrderDomain = {
    'schema': OrderSchema,
    'item_title': 'Main_Order to_factory',
    'resource_title':'factory/{factoryId}/order',
    # collection to store data
    'datasource': {
        'source': 'order'
    },
    # which API call allow to access order data
    'url': 'factory/<regex("[a-f0-9]{24}"):factoryInfo>/order',
    'mongo_indexes':{
        'factoryInfoIndexAsc':[('factoryInfo', 1)],
        'factoryInfoIndexDesc':[('factoryInfo', -1)]
    }
}