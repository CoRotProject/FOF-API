# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call

ProductOperationAndStatusSchema = {
    'operation':
    {
        'type': 'string',
        'required': True
    },
    'status':
    {
        'required': True,
        'type': 'string',
        'default': 'standBy',
        'allowed': ['standBy', 'toDo', 'doing', 'done']
    },
    'parameters':
    {
        'required': False,
        'type': 'list',
        'schema':{
            'type': 'string',
            'required': False,
        }
    },
}