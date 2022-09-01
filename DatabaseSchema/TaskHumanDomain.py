# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .TaskHumanSchema import *

TaskHumanDomain = {
    'schema': TaskHumanSchema,
    'item_title': 'Human Task in factory',
    'resource_title':'factory/{factoryId}/taskHuman',
    # collection to store data
    'datasource': {
        'source': 'task'
    },
    # which API call allow to access robot data
    'url': 'factory/<regex("[a-f0-9]{24}"):factoryInfo>/<regex("taskHuman"):taskType>',
}