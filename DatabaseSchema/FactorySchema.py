# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .PlanSchema import PlanSchema

FactorySchema = {
    'name':
    {
        'type': 'string',
        'required': True,
    },
    'plan':
    {
        'type': 'dict',
        'required': False,
        'schema': PlanSchema,
    },
}

