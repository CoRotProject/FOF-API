# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .TaskSchema import *

# TODO app.on_pre_POST_taskmoveproductxfromstockatostock += pre_post_taskmoveproductxfromstockatostock_post

TaskProduceSchema = dict(TaskSchema)
TaskProduceSchema.update({
    'taskType':
    {
        'type': 'string',
        'required': True,
        'default':'taskProduce'
    },
    'rawPartNames':
    {
        'type':'list',
        'required': True,
        'default': [],
        'schema':
        {
            # specify the DOMAIN name to access for checking
            'type': 'string',
            'required': False,
        }
    },
    'inputPartIds':
    {
        'type':'list',
        'required': True,
        'default': [],
        'schema':{
            'type': 'objectid',
            'required': True,
            'data_relation':
            {
                # specify the DOMAIN name to access for checking
                'resource': 'product',
                'embeddable': True
            },
        }
    },
    'taskName':
    {
        'type':'string',
        'required': True,
        'default':'default'
    },
    'endPartNames':
    {
        'type':'string',
        'required': True,
        'default':''
    },
})