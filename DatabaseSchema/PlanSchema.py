# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .Transform2DSchema import *

PlanSchema = {
    'picture':
    {
        'type':'string',
        'required': True,
    },
    'offset':
    {
        'type': 'dict',
        'required': True,
        'schema': Transform2DSchema,
    }, 
    'scale':
    {
        'type': 'float',
        'required': True,
        'default': 1,
    },
}