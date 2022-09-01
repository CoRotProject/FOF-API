# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call

# This schema can be merged with the TransformSchema by using x, y , and
Volume = {
    'dx': {
        'type': 'float',
        'required': False,
        'nullable': True,
        'default': 0
    },
    'dy': {
        'type': 'float',
        'required': False,
        'nullable': True,
        'default': 0
    },
    'dz': {
        'type': 'float',
        'required': False,
        'nullable': True,
        'default': 0
    },
}