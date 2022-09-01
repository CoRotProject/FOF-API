# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .TaskMoveProductXFromStockAToStockBSchema import *

TaskMoveProductXFromStockAToStockBDomain = {
    'schema': TaskMoveProductXFromStockAToStockBSchema,
    'item_title': 'MoveTask in factory',
    'resource_title':'factory/{factoryId}/taskMoveProductXFromStockAToStockB',
    # collection to store data
    'datasource': {
        'source': 'task'
    },
    # which API call allow to access robot data
    'url': 'factory/<regex("[a-f0-9]{24}"):factoryInfo>/<regex("taskMoveProductXFromStockAToStockB"):taskType>',
}