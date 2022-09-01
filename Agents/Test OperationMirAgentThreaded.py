#!/usr/bin/env python2 
# coding: utf8
# Copyright 2020 Fabrice DUVAL

from __future__ import unicode_literals
from __future__ import print_function
import time
import sys
import math
from FOF_API.Commandes import commandeAPI
#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

debugbaseenlocal = False
nomfactory = "Factory LINEACT Real"

if len(sys.argv) > 1 :
    nom = sys.argv[1]
else:
    nom = "mir100_Arm"

if debugbaseenlocal:
    commandeAPI.urlTemplateFactory = commandeAPI.urlTemplateFactory.replace('robigdata.rorecherche', '127.0.0.1')
    commandeAPI.urlTemplate = commandeAPI.urlTemplate.replace('robigdata.rorecherche', '127.0.0.1')

try:
    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
except IndexError:
    print("Base inacessible. Pause puis quitte")
    time.sleep(10)
    exit("Base non valide")

try:
    robotbase = commandeAPI.findINfactory(factoryid,"robot", name=nom)[0]
except IndexError:
    print("robot {} inacessible. Pause puis quitte".format(nom))
    time.sleep(10)
    exit("Robot non valide")

def dist(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2+(y1-y2)**2)


def createPoste(factoryid, nom, position):
    # taille poste 0.6 * 0.7 * 0.8
    # taille robot 0.6 * 1.0 * 0.4
    xrobot = position["x"]
    yrobot = position["y"]
    trobot = position["theta"] * math.pi / 180
    xmachine = xrobot + 0.8 * math.cos(trobot)
    ymachine = yrobot + 0.8 * math.sin(trobot)

    poste={}
    json = commandeAPI.createMachine(factoryid, nom, [], [], position={"x":xmachine, "y":ymachine, "theta":position["theta"], })
    poste["poste"] = json["_id"]

    commandeAPI.updateobject(factoryid,"machine",poste["poste"],{"volume":{"dx":0.6, "dy":0.7, "dz":0.8}})
    json = commandeAPI.createStock(factoryid, nom + " in", "in", position2d={"x":-0.8, "y":0.0, "theta":0.0, }, link=poste["poste"])
    poste["in"] = json["_id"]
    json = commandeAPI.createStock(factoryid, nom + " out", "out", position2d={"x":-0.8, "y":0.0, "theta":0.0, }, link=poste["poste"])
    poste["out"] = json["_id"]
    return poste

if __name__ == "__main__":
    Regenerationope = True
    print("Launch Robot Agent " + nom + " connected to database " + commandeAPI.urlTemplate)
    if Regenerationope:
        commandeAPI.deletepart(factoryid, typedata="operation", resourceInfo=robotbase)

    poste1 = createPoste(factoryid,"Poste test", {'x':12.40, 'y':-6.78, 'theta':90.49})

    operation1 = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (11.0, -10.0, 70.0))["_id"] # vertical
    operation2 = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (16.0, -4.0, -172.0), previous=operation1)["_id"] # vertical
    operation3 = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0.0, 0.0, 90.0, poste1["in"]), previous=operation2)["_id"] # vertical
    # operation3 = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0.0, 0.0, 90.0, poste1["in"]))["_id"] # vertical

    commandeAPI.updatestatus(factoryid, "operation", operation1, "toDo")
    commandeAPI.updatestatus(factoryid, "operation", operation2, "toDo")
    commandeAPI.updatestatus(factoryid, "operation", operation3, "toDo")

    print("end")
