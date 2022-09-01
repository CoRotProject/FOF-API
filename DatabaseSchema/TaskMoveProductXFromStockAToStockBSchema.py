# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .TaskSchema import *

# TODO app.on_pre_POST_taskmoveproductxfromstockatostock += pre_post_taskmoveproductxfromstockatostock_post

TaskMoveProductXFromStockAToStockBSchema = dict(TaskSchema)
TaskMoveProductXFromStockAToStockBSchema.update({
    'taskType':
    {
        'type': 'string',
        'required': True,
        'default':'taskMoveProductXFromStockAToStockB'
    },
    'stockAInfo':
    {
        'type':'objectid',
        'required': False,
        'data_relation':
        {
            # specify the DOMAIN name to access for checking
            'resource': 'stock',
            # make the factoryInfo embeddable with ?embedded={"stockAInfo":1}
            'embeddable': False
        }
    },
    'stockAInfoTxt':
    {
        'type':'string',
        'required': False,
    },
    'stockBInfo':
    {
        'type':'objectid',
        'required': False,
        'data_relation':
        {
            # specify the DOMAIN name to access for checking
            'resource': 'stock',
            # make the factoryInfo embeddable with ?embedded={"stockBInfo":1}
            'embeddable': True
        }
    },
    'stockBInfoTxt':
    {
        'type':'string',
        'required': False,
    },
    'productInfo':
    {
        'type':'objectid',
        'required': True,
        'data_relation':
        {
            # specify the DOMAIN name to access for checking
            'resource': 'product',
            # make the factoryInfo embeddable with ?embedded={"productInfo":1}
            'embeddable': True
        }
    }
})