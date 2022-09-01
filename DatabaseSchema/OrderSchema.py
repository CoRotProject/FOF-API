# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .ElementSchema import *

OrderSchema = dict(ElementSchema)
OrderSchema.update({
    # reference of the product
    'name':
    {
        'type': 'string',
        'required': True,
    },
    # Designation of the products
    'productToDo': 
    {
        'type': 'string',
        'required': True,
    },
    'quantity':
    {
        'type': 'integer',
        'default': 1,
        'required': True,
    },
    'orderStatus':
    {
        'type': 'string',
        'allowed': ['toDo', 'toDoAcknowledge', 'toDoSplitedIntoJobs', 'doing', 'done', 'error'],
        'default': 'toDo',
        'required': True
    },
    'jobList': 
    {
        'type': 'list',
        'required': True,
        'default':[],
        'schema':
        {
            'type': 'objectid',
            'required': True,
            'data_relation':
            {
                # specify the DOMAIN name to access for checking
                'resource': 'job',
                # make the resourceInfo embeddable with ?embedded={"operationInfoList":1}
                'embeddable': True
            }
        }
    },
})