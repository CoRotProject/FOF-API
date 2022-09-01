# XxxSchema file controls how the data must be organized
# XxxDomain file configures how to access data throught URL API call
from .TaskProduceSchema import *

# TODO app.on_pre_POST_taskmoveproductxfromstockatostock += pre_post_taskmoveproductxfromstockatostock_post

TaskHumanSchema = dict(TaskProduceSchema)
TaskHumanSchema.update({
    'taskType':
    {
        'type': 'string',
        'required': True,
        'default':'taskHuman'
    },
    'taskstodo':
    {
        'type': 'list',
        'required': True,
        'default':[],
        'schema':{
			'type': 'string',
			'required': False,
		}
    },
})