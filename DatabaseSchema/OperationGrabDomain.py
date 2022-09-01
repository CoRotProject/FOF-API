# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .OperationGrabSchema import *

OperationGrabDomain = {
    'schema': OperationGrabSchema,
    'item_title': 'Grab action in factory',
    'resource_title':'factory/{factoryId}/grab',
    # collection to store data
    'datasource': {
        'source': 'operation'
    },
    # which API call allow to access robot data
    'url': 'factory/<regex("[a-f0-9]{24}"):factoryInfo>/<regex("grab"):operationType>'
}