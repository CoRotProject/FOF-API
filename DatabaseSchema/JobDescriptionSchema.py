# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call


from .ElementSchema import *

# extends the FactoryElementSchema
JobDescriptionSchema = dict(ElementSchema)
JobDescriptionSchema.update({
    # the type of task. This value will be overridden by Child Task defined
    'taskList':
    {
        'type': 'list',
        'required': True,
        'default':[],
        'schema':
        {
            'type': 'objectid',
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