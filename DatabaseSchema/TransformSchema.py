# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call

TransformSchema = {
    'position':
    {
        'type': 'dict',
        'required': False,
        'nullable': True,
        'schema':
        {
            'x': {'type': 'float', 'default': 0},
            'y': {'type': 'float', 'default': 0},
            'z': {'type': 'float', 'default': 0},
        }
    },
    'rotation':
    {
        'type': 'dict',
        'required': False,
        'nullable': True,
        'schema':
        {
            'qx': {'type': 'float', 'default': 0},
            'qy': {'type': 'float', 'default': 0},
            'qz': {'type': 'float', 'default': 0},
            'qw': {'type': 'float', 'default': 0},
        }
    }
}