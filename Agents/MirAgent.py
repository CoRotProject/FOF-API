#!/usr/bin/env python2 
# coding: utf8
# Copyright 2021 Fabrice DUVAL

from __future__ import unicode_literals
from __future__ import print_function
import time
# import sys
# import os
# import glob
# import threading
import imp
import queue
import mir
import sys
import OperationAgent
import Agentrobotmove_mir as agentmove

import Commandes.commandeAPI as commandeAPI
#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()
    
# Syntaxe
# MirAgent url robotname
# url : full url of API (ex: http://robigdata.rorecherche:5000/)
# robotname name of the robot on the database

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

try:
    nomrobot = sys.argv[2]
except IndexError:
    nomrobot = "mir100_Arm"

try:
    nomfactory = sys.argv[3]
except IndexError:
    nomfactory = "Factory LINEACT Real"

try:
    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
except IndexError:
    print("Base inacessible. Pause puis quitte")
    time.sleep(10)
    exit("Base non valide")

try:
    robotbase = commandeAPI.findINfactory(factoryid, "robot", name=nomrobot)[0]
except IndexError:
    print("robot {} inacessible. Pause puis quitte".format(nomrobot))
    time.sleep(10)
    exit("Robot non valide")

def testmove():
    """lance 4 points pour tests de commmunication"""
    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
    robot = commandeAPI.findINfactory(factoryid, "robot", name=nomrobot)[0]
    a1 = commandeAPI.createOperationMoveRobotTo(factoryid, robot, (11.77, -6.16, 4.0))["_id"]
    a2 = commandeAPI.createOperationMoveRobotTo(factoryid, robot, (16.53, 2.11, 90.88), previous=a1)["_id"]
    a3 = commandeAPI.createOperationMoveRobotTo(factoryid, robot, (35.02, 3.19, 7.01), previous=a1)["_id"]
    a4 = commandeAPI.createOperationMoveRobotTo(factoryid, robot, (30.60, -4.59, -65.73), previous=a1)["_id"]
    commandeAPI.updateobject(factoryid, "operation", a1, {"nextOperationInfo":a4})
    for operation in commandeAPI.findINfactory(factoryid, "operation", status="standBy"):
        commandeAPI.updatestatus(factoryid, "operation", operation, "toDo")

if __name__ == "__main__":
    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
    deleteope = False
    createop = False


    print("Launch Operation Agent " + nomrobot + commandeAPI.urlTemplate)
    resource = commandeAPI.findINfactory(factoryid, "resource", name=nomrobot)[0]
    if deleteope:
        commandeAPI.deletepart(factoryid, typedata="operation", resourceInfo=resource)
    if createop:
        testmove()

    try: # fonctionne sur le robot ou pas ?
        imp.find_module('rospy')
        robotreel = mir.Mir(nom=nomrobot)
    except ImportError:
        robotreel = mir.Mir(nom=nomrobot, lienhttp='http://mir_arm.rorecherche/ajax/')

    # create communication FIFO
    fiforobotmove = queue.Queue() # create FIFO of valide operation
    fiforetrobotmove = queue.Queue() # create FIFO of return value for database
    fifoop = {"robotmove":fiforobotmove,}
    fiforet = {"robotmove":fiforetrobotmove,}

    opagent = OperationAgent.AgentOperation(1, nomfactory+" "+nomrobot, factoryid, resource, nomrobot, ["robotmove"], fifoop, fiforet)
    robot_agent = agentmove.AgentDeplacement(nomfactory+" "+nomrobot, factoryid, robotreel, fiforobotmove, fiforetrobotmove)

    opagent.start()
    robot_agent.start()
    print("done")
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        opagent.terminate()
        robot_agent.terminate()
    print("killed")