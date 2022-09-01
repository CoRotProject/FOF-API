# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
# description des ressources :
# robot : robot mobile ou bras
# machine : chaine de production ou equivalent (plusieurs in/out et fonctions)
# human : humain
# meta : Meta ressource constituée de robot/machine/human
# misc : no déterminé


from .ElementSchema import *
from .ResourceCapabilitySchema import *

# extends the FactoryElementSchema
ResourceSchema = dict(ElementSchema)
ResourceSchema.update({
    'resourceType':
    {
        'type': 'string',
        'allowed':['robot', 'machine', 'human', 'meta', 'misc'],   # TO KEEP ADDING AS YOU ADD A PARTICULAR RESOURCE...
        'required': True,
    },
    'resourceCapabilityList':
    {
        'type': 'list',
        'nullable': True,
        'default': None,
        'required': True,
        'schema':
        {
            'type': 'dict',
            'nullable': True,
            'schema':ResourceCapabilitySchema
        }
    },
    'status':
    {
        'type': 'string',
        'allowed': ['offline', 'free', 'internalProcess', 'busy', 'error', 'in_meta'],
        'default': 'offline',
        'required': True
    },
    'currentOperationList':
    {
        'type': 'objectid',
        'nullable': True,
        'default': None,
        'required': False,
        'data_relation':
        {
            # specify the DOMAIN name to access for checking
            'resource': 'operation',
            # make the currentOperationInfo embeddable with ?embedded={"currentOperationInfo":1}
            'embeddable': True
        }
    }, #TODO CurrentTaksListSchema
    
    # allow to put whatever it needs for each resource
    'internalParams':
    {
        'type': 'dict',
        'nullable': True, 
        'default': None,
        'required': False
    },
    'link': {
        'type': 'objectid',
        'required': False,
        # physical link between stock and other objet in factory
        # position is defined in function of the linked object
        # referential integrity constraint: value must exist in the 'factory' collection. Since we aren't declaring a 'field' key,
        # will default to `factory._id` (or, more precisely, to whatever ID_FIELD value is).
        'data_relation':
        {
            # specify the DOMAIN name to access for checking
            'resource': 'resource',
            # make the link embeddable with ?embedded={"link":1}
            'embeddable': True
        }
    },
})