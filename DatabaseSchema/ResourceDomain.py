# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
# This Domain allow to access all the resource in one call
from .ResourceSchema import *

ResourceDomain = {
    'schema': ResourceSchema,
    'item_title': 'Resource in factory',
    'resource_title':'factory/{factoryId}/resource',
    # collection to store data
    'datasource': {
        'source': 'resource'
    },
    # which API call allow to access data
    'url': 'factory/<regex("[a-f0-9]{24}"):factoryInfo>/resource',
    #Ce principe foncionne pour pouvoir ajouter une ressource d'un certain type ajouter un paramètre pour pouvoir récupérer par resourceType 
    #'url': 'factory/<regex("[a-f0-9]{24}"):factoryInfo>/<regex("\w+"):resourceType>',
    # create index for filtering faster
    'mongo_indexes':{
        'resourceTypeIndexAsc':[('resourceType', 1)],
        'resourceTypeIndexDes':[('resourceType', -1)],
        'factoryAsc':[('factoryInfo', 1)],
        'factoryDes':[('factoryInfo', -1)]
    }
}