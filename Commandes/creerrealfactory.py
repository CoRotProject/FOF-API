# coding: utf8
# Copyright 2020 Fabrice DUVAL
# import requests
import os
import sys
# import random
import base64
# from pyquaternion import Quaternion

import commandeAPI

#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()
print(os.getcwd())
print(base64.b64decode(base64.b64encode(b"Base 64 Valide")))

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

def createRobot(factoryid, nom, typerobot, capacites):
    robot={}
    json = commandeAPI.createRobotResource(factoryid, nom, typerobot,capacites)
    robot["robot"] = json["_id"]
    json = commandeAPI.createStock(factoryid, nom + " in", "in", link=robot["robot"])
    robot["in"] = json["_id"]
    json = commandeAPI.createStock(factoryid, nom + " out", "out", link=robot["robot"])
    robot["out"] = json["_id"]
    return robot

if __name__ == "__main__":
    Regeneration = True
    Newfactoryid = False
    renewmap = False
    nommap = "..\\Visualisation\\Madrillet.png"
    scalemap = [(-20.5, -34.2, 0.0), 0.05]
    print(commandeAPI.urlTemplate)
    print(commandeAPI.urlTemplateFactory)
    nomfact = "Factory LINEACT Real"
    if Regeneration:
        # etape affacement de l'ancienne base
        listeinbase = commandeAPI.findfactory(name=nomfact)
        # listeinbase = findfactory(name="Factory LINEACT Test")
        effaceFactory = (len(listeinbase) != 1)  or Newfactoryid
        for usine in listeinbase:
            commandeAPI.deletepart(usine,typedata="resource")                           # database resource
            commandeAPI.deletepart(usine,typedata="product")                            # database product
            commandeAPI.deletepart(usine,typedata="taskMoveProductXFromStockAToStockB") # database task 1/2
            commandeAPI.deletepart(usine,typedata="taskProduce")                        # database task 2/2
            commandeAPI.deletepart(usine,typedata="stock")                              # database stock
            commandeAPI.deletepart(usine,typedata="operation")                          # database operation
            commandeAPI.deletepart(usine,typedata="job")                                # database job
            commandeAPI.deletepart(usine,typedata="jobdescription")                     # database jobdescription
            commandeAPI.deletepart(usine,typedata="order")                              # database order
            commandeAPI.deletepart(usine,typedata="machine")                            # database machine
            if effaceFactory:
                commandeAPI.deletepart(usine)
        if effaceFactory:
            json = commandeAPI.createFactory(nomfact)
            factoryid = json["_id"]
        else:
            factoryid = usine



        commandeAPI.mapinfactory(factoryid, nommap, scalemap[0], scalemap[1])

        mirArm = createRobot(factoryid, "mir100_Arm", "mir100", [{"category": "transport"},{"category": "wait"}])
        mirCapitaine = createRobot(factoryid, "mir100_Capitaine", "mir100", [{"category": "transport"},{"category": "wait"}])
        ur10 = createRobot(factoryid, "ur10_t", "ur10", [{"category": "grab"},{"category": "wait"}])
        # ur5 = createRobot(factoryid, "ur5_t_e", "ur5", [{"category": "grab"},{"category": "wait"}])
        waffle03 = createRobot(factoryid, "waffle_03", "turtlew", [{"category": "transport"},{"category": "wait"}])

        commandeAPI.updateRobotPoseRandom(factoryid, mirArm["robot"])
        commandeAPI.updateRobotPoseRandom(factoryid, mirCapitaine["robot"])
        commandeAPI.updateRobotPoseRandom(factoryid, ur10["robot"])
        commandeAPI.updateRobotPoseRandom(factoryid, waffle03["robot"])
        
        # commandeAPI.updateRobotPoseRandom(factoryid, ur5["robot"])

        json = commandeAPI.createHumanResource(factoryid, "Fabrice", "operator" , [{"category": "transport"},{"category": "wait"},{"category": "grab"}])
        Fabrice = json["_id"]
        json = commandeAPI.createHumanResource(factoryid, "M'hammed", "operator", [{"category": "transport"},{"category": "wait"},{"category": "grab"}])
        Mhammed = json["_id"]
    else:
        factoryid = commandeAPI.findfactory(name=nomfact)[0]
        if renewmap:
            commandeAPI.mapinfactory(factoryid, nommap, scalemap[0], scalemap[1])

    print("done")
