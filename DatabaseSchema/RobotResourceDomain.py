# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call

from .RobotResourceSchema import *

RobotResourceDomain = {
    'schema': RobotResourceSchema,
    'item_title': 'Robot in factory',
    'resource_title':'factory/{factoryId}/robot',
    # collection to store data
    'datasource': {
        'source': 'resource'
    },
    # which API call allow to access robot data
    'url': 'factory/<regex("[a-f0-9]{24}"):factoryInfo>/<regex("robot"):resourceType>',

    'mongo_indexes':{
        'robotTypeIndexAsc':[('robotType', 1)],
        'robotTypeIndexDesc':[('robotType', -1)]
    }
}