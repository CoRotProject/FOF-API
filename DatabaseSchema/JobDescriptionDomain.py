# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .JobDescriptionSchema import *

JobDescriptionDomain = {
    'schema': JobDescriptionSchema,
    'item_title': 'Job description (Task list) in factory',
    'resource_title':'factory/{factoryId}/jobdescription',
    # collection to store data
    'datasource': {
        'source': 'jobdescription'
    },
    # which API call allow to access TaskList data
    'url': 'factory/<regex("[a-f0-9]{24}"):factoryInfo>/jobdescription',
    'mongo_indexes':{
        'factoryInfoIndexAsc':[('factoryInfo', 1)],
        'factoryInfoIndexDesc':[('factoryInfo', -1)]
    }
}