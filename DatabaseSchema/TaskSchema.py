# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call


from .ElementSchema import *

# extends the FactoryElementSchema
TaskSchema = dict(ElementSchema)
TaskSchema.update({
    # the type of task. This value will be overridden by Child Task defined
    'taskType':
    {
        'type': 'string',
        'required': True,
        'default':'Task'
    },
    'status':
    {
        'type': 'string',
        'allowed': ['standBy', 'toDo', 'toDoAcknowledge', 'doing', 'done', 'error'],
        'default': 'standBy',
        'required': True
    },
    'operationInfoList':
    {
        'type': 'list',
        'required': True,
        'default': [],
        'schema':
        {
            'type': 'objectid',
            'required': True,
            'data_relation':
            {
                # specify the DOMAIN name to access for checking
                'resource': 'operation',
                # make the resourceInfo embeddable with ?embedded={"operationInfoList":1}
                'embeddable': True
            }
        }
    },
    'resourceInfo':
    {
        'type': 'objectid',
        'required': False,
        'data_relation':
        {
        #     # specify the DOMAIN name to access for checking
            'resource': 'resource',
        #     # make the resourceInfo embeddable with ?embedded={"operationInfoList":1}
            'embeddable': True
        }
    },
    'nextTaskInfo':
    {
        'type': 'objectid',
        'nullable': True,
        'default': None,
        'required': False,
        'data_relation':
        {
            # specify the DOMAIN name to access for checking
            'resource': 'task',
            # make the resourceInfo embeddable with ?embedded={"operationInfoList":1}
            'embeddable': True
        }
    },
    'precedenceTaskInfo':
    {
        'type': 'list',
        'default': [],
        'required': True,
        'schema':{
            'type': 'objectid',
            'nullable': True,
            'default': None,
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
    # _created is existing by default
    #TODO UPDATE BY THE API CALL when status is changed
    'dateAcknowledgement': { 'type': 'datetime' }, 
    'dateDoing': { 'type': 'datetime' },
    'dateDone': { 'type': 'datetime' }
})