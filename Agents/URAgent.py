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
import UR as robot_arm
import sys
import json
import OperationAgent
import AgentGrab_UR as agentgrab

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
    nomfactory = sys.argv[2]
except IndexError:
    nomfactory = "Factory LINEACT Real"

try:
    nomrobot = sys.argv[3]
    Robot = robot_arm.arm(host=sys.argv[4])
except IndexError:
    nomrobot = "ur10_t"
    Robot = robot_arm.arm(hote="10.191.76.119")

try:
    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
except IndexError:
    print("Base inacessible. Pause puis quitte")
    time.sleep(3)
    exit("Base non valide")

try:
    robotbase = commandeAPI.findINfactory(factoryid, "robot", name=nomrobot)[0]
except IndexError:
    print("robot {} inacessible. Pause puis quitte".format(nomrobot))
    time.sleep(3)
    exit("Robot non valide")

def testmove():
    """lance 4 points pour tests de commmunication"""
    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
    robot = commandeAPI.findINfactory(factoryid, "robot", name=nomrobot)[0]
    commandeAPI.deletepart(factoryid, "operation", commandeAPI.findINfactory(factoryid, "operation", resourceInfo=robot))
    a1 = commandeAPI.createOperationGrab(factoryid, robot, [[0.0, 0.9, 0.2], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="grab", functionparameters=json.dumps({"delta_saisie":0.10}), name="op1")["_id"] # vertical
    a2 = commandeAPI.createOperationGrab(factoryid, robot, [[0.0, 0.9, 0.2], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="grab", functionparameters=json.dumps({"delta_saisie":0.1}), name="op2", previous=a1)["_id"] # vertical
    a3 = commandeAPI.createOperationGrab(factoryid, robot, [[0.0, 0.9, 0.2], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="grab", functionparameters=json.dumps({"delta_saisie":0.20}), name="op3", previous=a1)["_id"] # vertical
    a4 = commandeAPI.createOperationGrab(factoryid, robot, [[0.0, 0.9, 0.2], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="grab", functionparameters=json.dumps({"delta_saisie":0.5}), name="op4", previous=a1)["_id"] # vertical
    commandeAPI.updateobject(factoryid, "operation", a1, {"nextOperationInfo":a4})
    for operation in commandeAPI.findINfactory(factoryid, "operation", status="standBy", resourceInfo=robot):
        commandeAPI.updatestatus(factoryid, "operation", operation, "toDo")

if __name__ == "__main__":
    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
    deleteope = False
    createop = True


    print("Launch Operation Agent " + nomrobot + commandeAPI.urlTemplate)
    resource = commandeAPI.findINfactory(factoryid, "resource", name=nomrobot)[0]
    if deleteope:
        commandeAPI.deletepart(factoryid, typedata="operation", resourceInfo=resource)
    if createop:
        testmove()

    try: # fonctionne sur le robot ou pas ?
        test = Robot.lire_statut()
        print(test["Program_state"])
    except ImportError:
        print("Pas de robot")
        exit("Robot introuvable")

    # create communication FIFO
    fiforobotgrab = queue.Queue() # create FIFO of valide operation
    fiforetrobotgrab = queue.Queue() # create FIFO of return value for database
    fifoop = {"grab":fiforobotgrab,}
    fiforet = {"grab":fiforetrobotgrab,}

    opagent = OperationAgent.AgentOperation(1, nomfactory+" "+nomrobot, factoryid, resource, nomrobot, ["grab"], fifoop, fiforet)
    robot_agent = agentgrab.AgentGrab(nomfactory+" "+nomrobot, factoryid, Robot, fiforobotgrab, fiforetrobotgrab)

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