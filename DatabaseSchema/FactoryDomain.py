# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call

from .FactorySchema import *

FactoryDomain = {
    #'datasource': {
    #    'source': 'factoryTest'
    #},
    'item_title': 'factory',
    'schema': FactorySchema,
    'additional_lookup':
    {
        'url': 'regex("\w+")',
        'field': 'name'
    }
}