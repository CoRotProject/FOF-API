# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .OperationHumanSchema import *

OperationHumanDomain = {
    'schema': OperationHumanSchema,
    'item_title': 'Human Operation in factory',
    'resource_title':'factory/{factoryId}/humanaction',
    # collection to store data
    'datasource': {
        'source': 'operation'
    },
    # which API call allow to access human data
    'url': 'factory/<regex("[a-f0-9]{24}"):factoryInfo>/<regex("humanaction"):operationType>'

}