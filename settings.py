"""
    NOTE:
        We don't need to create the two collections in MongoDB.

        Actually, we don't even need to create the database:
        GET requests on an empty/non-existant DB will be served correctly ('200' OK with an empty collection);
        DELETE/PATCH will receive appropriate responses ('404' Not Found),
        and POST requests will create database and collections when needed.

        Keep in mind however that such an auto-managed database will most likely
        perform poorly since it lacks any sort of optimized index.
"""

import os
import sys
# import socket
from DatabaseSchema.FactoryDomain import *
from DatabaseSchema.ResourceDomain import *
from DatabaseSchema.RobotResourceDomain import *
from DatabaseSchema.MachineResourceDomain import *
from DatabaseSchema.HumanResourceDomain import *
from DatabaseSchema.MetaResourceDomain import *
# from DatabaseSchema.StockProductDomain import *
# from DatabaseSchema.StockPartDomain import *
from DatabaseSchema.StockDomain import *
from DatabaseSchema.ProductDomain import *
from DatabaseSchema.JobDescriptionDomain import *
from DatabaseSchema.OrderDomain import *
from DatabaseSchema.JobDomain import *
from DatabaseSchema.TaskDomain import *
from DatabaseSchema.TaskProduceDomain import *
from DatabaseSchema.TaskMoveProductXFromStockAToStockBDomain import *
from DatabaseSchema.TaskHumanDomain import *
from DatabaseSchema.OperationDomain import *
from DatabaseSchema.OperationHumanDomain import *
from DatabaseSchema.OperationMoveRobotToDomain import *
from DatabaseSchema.OperationGrabDomain import *
from DatabaseSchema.OperationMachineDomain import *


#TODO manage configuration on PROD Vs DEV environment
#TODO create a user


MONGO_HOST="127.0.0.1"
if len(sys.argv) > 2:
    # need argument in order to run for any computer on network
    print('run with 2nd argument Mongodb url',sys.argv[2])
    if not False in [c in "abcedfghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789." for c in sys.argv[2]]:
        MONGO_HOST = sys.argv[2]
    else:
        print("need IP or DNS adresse")
        exit()

# MONGO_HOST="10.191.76.25"
MONGO_PORT = 27017
MONGO_USERNAME = ''
MONGO_PASSWORD = ''
MONGO_DBNAME = 'FOF'

DEBUG = True

# RATE_LIMIT_GET = (3, 60 * 15)  - rate limit does not work...


# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide read-only access to the endpoint).
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']

# Enable reads (GET), edits (PATCH) and deletes of individual items (defaults to read-only item access).
ITEM_METHODS = ['GET', 'PUT', 'PATCH', 'DELETE']

# We enable standard client cache directives for all resources exposed by the API. We can always override these global settings later.
CACHE_CONTROL = 'max-age=20'
CACHE_EXPIRES = 20

# If False, disable _links in the answer 
HATEOAS = True

# disable the ETAG checking with the If-Match Header
IF_MATCH = False

# Can change the name of the following fields: "_created" or "_updated" or "_id"
# DATE_CREATED
# LAST_UPDATED
# ID_FIELD

# to save bandwidth = only returns a set of fields
# BANDWIDTH_SAVER
factory = FactorySchema

# The DOMAIN dict explains which resources will be available and how they will be accessible to the API consumer.
DOMAIN = {
    'factory': FactoryDomain,
    'resource': ResourceDomain,
    'robot': RobotResourceDomain,
    'machine': MachineResourceDomain,
    'human': HumanResourceDomain,
    'meta' : MetaResourceDomain,
    # 'stockPart': StockPartDomain,
    # 'stockProduct': StockProductDomain,
    'stock':StockDomain,
    # 'part': part,
    'JobDescription': JobDescriptionDomain,
    'product': ProductDomain,
    'order': OrderDomain,
    'job': JobDomain,
    'task': TaskDomain,
    'taskMoveProductXFromStockAToStockB': TaskMoveProductXFromStockAToStockBDomain,
    'taskProduce': TaskProduceDomain,
    'taskHuman': TaskHumanDomain,
    'operation':OperationDomain,
    'operationHuman':OperationHumanDomain,
    'operationMoveRobotTo':OperationMoveRobotToDomain,    # 'operation': operation
    'operationGrab':OperationGrabDomain,
    'operationMachine':OperationMachineDomain,
}
