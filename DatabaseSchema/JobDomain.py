# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .JobSchema import *

JobDomain = {
    'schema': JobSchema,
    'item_title': 'Main_Order to_factory',
    'resource_title':'factory/{factoryId}/job',
    # collection to store data
    'datasource': {
        'source': 'job'
    },
    # which API call allow to access job data
    'url': 'factory/<regex("[a-f0-9]{24}"):factoryInfo>/job',
    'mongo_indexes':{
        'factoryInfoIndexAsc':[('factoryInfo', 1)],
        'factoryInfoIndexDesc':[('factoryInfo', -1)]
    }
}