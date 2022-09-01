# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .ElementSchema import *

JobSchema = dict(ElementSchema)
JobSchema.update({
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
    'jobStatus': # unknown status is when the job archetype does not exist in database jobdescription
    {
        'type': 'string',
        'allowed': ['toDo', 'toDoAcknowledge', 'unknown', 'doing', 'done', 'error'],
        'default': 'toDo',
        'required': True
    },
    'taskList': 
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
                'resource': 'task',
                # make the resourceInfo embeddable with ?embedded={"operationInfoList":1}
                'embeddable': True
            }
        }
    },
})