# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .OperationSchema import *

OperationDomain = {
    'schema': OperationSchema,
    'item_title': 'operation in factory',
    'resource_title':'factory/{factoryId}/operation',
    # collection to store data
    'datasource': {
        'source': 'operation'
    },
    # which API call allow to access robot data
    'url': 'factory/<regex("[a-f0-9]{24}"):factoryInfo>/operation',
    'mongo_indexes':{
        'factoryInfoIndexAsc':[('factoryInfo', 1)],
        'factoryInfoIndexDesc':[('factoryInfo', -1)]
    }
}