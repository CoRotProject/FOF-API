# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .TaskSchema import *

TaskDomain = {
    'schema': TaskSchema,
    'item_title': 'Task in factory',
    'resource_title':'factory/{factoryId}/task',
    # collection to store data
    'datasource': {
        'source': 'task'
    },
    # which API call allow to access robot data
    'url': 'factory/<regex("[a-f0-9]{24}"):factoryInfo>/task',
    # # task are only readable, for writing them, you must use 
    # # the SubClass of Task Like TaskMoveProductXFromStockAToStockB
    # 'resource_methods' : ['GET'],
    # 'item_methods' : ['GET'],
    ## Supprimé pour des raisons techniques de traitement en groupe des taches
    'mongo_indexes':{
        'factoryInfoIndexAsc':[('factoryInfo', 1)],
        'factoryInfoIndexDesc':[('factoryInfo', -1)]
    }
}