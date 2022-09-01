# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call

# This schema can be merged with the TransformSchema by using x, y , and
Transform2DSchema = {
    'x': {
        'type': 'float',
        'required': False,
        'nullable': True,
        'default': 0
    },
    'y': {
        'type': 'float',
        'required': False,
        'nullable': True,
        'default': 0
    },
    'theta': {
        'type': 'float',
        'required': False,
        'nullable': True,
        'default': 0
    },
}