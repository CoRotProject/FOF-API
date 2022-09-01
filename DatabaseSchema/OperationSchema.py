# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call

from .ElementSchema import *

# extends the FactoryElementSchema
OperationSchema = dict(ElementSchema)
OperationSchema.update({
    'name': # stop the name requirement herited from FactoryElementSchema
    {
        'required':False,
        'default':''
    },
    # the type of task. This value will be overridden by Child Task defined
    'operationType':
    {
        'type': 'string',
        'allowed': ['production', 'grab', 'robotmove', 'humanaction', 'none'],
        'required': True,
        'default':'operation'
    },
    'status':
    {
        'type': 'string',
        'allowed': ['standBy','toDo', 'toDoAcknowledge', 'doing', 'done', 'error'],
        'default': 'standBy',
        'required': True
    },
    'resourceInfo':
    {
        'type': 'objectid',
        'required': True,
        'data_relation':
        {
        #     # specify the DOMAIN name to access for checking
            'resource': 'resource',
        #     # make the resourceInfo embeddable with ?embedded={"operationInfoList":1}
            'embeddable': True
        }
    },
    'nextOperationInfo':
    {
        'type': 'objectid',
        'nullable': True,
        'default': None,
        'required': False,
        'data_relation':
        {
            # specify the DOMAIN name to access for checking
            'resource': 'operation',
            # make the resourceInfo embeddable with ?embedded={"operationInfoList":1}
            'embeddable': True
        }
    },
    'precedenceOperationInfo':
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
                'resource': 'operation',
                # make the resourceInfo embeddable with ?embedded={"operationInfoList":1}
                'embeddable': True
            }
        }
    },
    'canDoThisOperation': 
    {
        'type':'boolean',
        'default':True
    },
    # _created is existing by default
    #TODO UPDATE BY THE API CALL when status is changed
    'dateAcknowledgement': { 'type': 'datetime' }, 
    'dateDoing': { 'type': 'datetime' },
    'dateDone': { 'type': 'datetime' },
    'params':{} # depends on the type of operation
})