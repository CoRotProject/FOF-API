# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .ResourceSchema import *

RobotResourceSchema = dict(ResourceSchema)
RobotResourceSchema.update({
    'resourceType': # override from FactoryResourceSchema
    {
        'type': 'string',
        'allowed':['robot'],   # TO KEEP ADDING AS YOU ADD A PARTICULAR RESOURCE...
        'required': True,
        'default': 'robot'
    },
    # turttlew ==> Turttle3 Pi3 Waffle
    # turttleb ==> Turttle3 Pi3 Burger
    'robotType':
    {
        'type': 'string',
        'allowed': ['mir100', 'ur10', 'ur5', 'robotnik', 'turtlew', 'turtleb', 'ceriagv', 'ceriarm', ],
        'required': True
    },
    # list of product on it
    'productInfoList':
    {
        'type':'list',
        'nullable': True,
        'default': None,
        'required': False,
        'schema':
        {
            'type': 'objectid',
            'data_relation':
            {
                # specify the DOMAIN name to access for checking
                'resource': 'product',
                'embeddable': True
            }
        }
    }
})