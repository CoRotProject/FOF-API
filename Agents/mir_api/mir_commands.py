#!/usr/bin/env python2 
# coding: utf8
"""
authors: Ayman DAMOUN  
request FOF-API for the new operation 
"""

import requests, json
from FOF_API.Commandes import commandeAPI
from Agentrobotmove_mir import AgentDeplacement
from UpdatePosMir import RobotParamUpdater
import os
import sys
import base64
import queue
import OperationAgent
import time
from mir_utils import mymir

#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()
print(os.getcwd())
print(base64.b64decode(base64.b64encode(b"Base 64 Valide")))

try:
    if len(sys.argv) > 1:
        print("API in remote mode: ",sys.argv[1])
        commandeAPI.seturl(sys.argv[1])
    else:
        print("API in remote mode: ","http://robigdata.rorecherche:5000/")
        commandeAPI.seturl("http://robigdata.rorecherche:5000/")
except IndexError:
    print("API in local 127.0.0.1")

# get Request
Regeneration = True
Newfactoryid = False
renewmap = False
nommap = "../FOF_API/Visualisation/Madrillet.png"
scalemap = [(-20.5, -34.2, 0.0), 0.05]
print(commandeAPI.urlTemplate)
print(commandeAPI.urlTemplateFactory)
nomfact = "smart factory lab lineact"
nomrobot = "mir100_Arm"
factoryid = commandeAPI.findfactory(name=nomfact)[0]
robotId = commandeAPI.findINfactory(factoryid,"robot", name=nomrobot)
MirIp = '10.191.76.55'
robotreel = mymir(MirIp)
Mir100 = commandeAPI.findINfactory(factoryid,"robot", name=nomrobot)[0]
# create communication FIFO
fiforobotmove = queue.Queue() # create FIFO of valide operation
fiforetrobotmove = queue.Queue() # create FIFO of return value for database
fifoop = {"robotmove":fiforobotmove,}
fiforet = {"robotmove":fiforetrobotmove,}
resource = commandeAPI.findINfactory(factoryid, "resource", name=nomrobot)[0]
opagent = OperationAgent.AgentOperation(1, nomfact+" "+nomrobot, factoryid, resource, nomrobot, ["robotmove"], fifoop, fiforet)
robot_agent = AgentDeplacement(nomfact+" "+nomrobot, factoryid, robotreel, fiforobotmove, fiforetrobotmove)
robot = RobotParamUpdater(robotreel, factoryid, Mir100)
time.sleep(30)
opagent.start()
robot_agent.start()
robot.start()

print("done")
try:
    while True:
        time.sleep(10)
except (KeyboardInterrupt, SystemExit):
    opagent.terminate()
    robot_agent.terminate()
    robot.terminate()
print("killed")

'''
    operationId = commandeAPI.findINfactory(factoryid, "operation", resourceInfo=robotId[0])
    #print(operationId)
    operationvalues=commandeAPI.getvalues(factoryid, "operation", operationId[0])
    print(operationvalues)
    print(operationvalues['params']["transform2D"]["x"])
i=0
operationinfo = []
for x in operationId:
    operationinfo.append(commandeAPI.getvalues(factoryid, "operation", x))
    i=+1
print(operationinfo[0]["name"])
idddd= operationinfo[1]["name"]

MirIp = '10.191.76.55'
host = 'http://'+MirIp+'/api/v2.0.0/'
headers = {}
headers['Content-Type'] = 'application/json'
headers['Authorization'] = 'Basic YWRtaW46NzkzNWUyZGJkYzExMWZkYjhkOTExNjFjMzI3Y2UxNDhhMTRkZDc5MGUxM2Q1MWE5ZjFhMTk3ZTA0M2VhN2QwZg=='

get_missions = requests.get(host+'missions',headers=headers)
status = requests.get(host+'status',headers=headers)
#print(get_missions.status_code)
#print(get_missions.text)

Go_forward_80cm_id = {"mission_id": "77d93590-df23-11eb-84a7-f44d306ef93b"}
Go_backward_80cm_id = {"mission_id": "9c5f96b2-df22-11eb-84a7-f44d306ef93b"}
test = {"mission_id": idddd}
post_mission =requests.post(host+'mission_queue',json = test, headers = headers)

print(post_mission)
'''
