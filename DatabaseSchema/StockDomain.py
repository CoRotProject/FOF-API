# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .StockSchema import *

StockDomain = {
    'schema': StockSchema,
    'item_title': 'Stock in factory',
    'resource_title':'factory/{factoryId}/stock',
    # collection to store data
    'datasource': {
        'source': 'stock'
    },
    # which API call allow to access robot data
    'url': 'factory/<regex("[a-f0-9]{24}"):factoryInfo>/stock',

    'mongo_indexes':{
        'stockTypeIndexAsc':[('stockType', 1)],
        'stockTypeIndexDesc':[('stockType', -1)],
        'factoryInfoIndexAsc':[('factoryInfo', 1)],
        'factoryInfoIndexDesc':[('factoryInfo', -1)]
    }
}