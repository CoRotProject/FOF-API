# coding: utf8
# Copyright 2020 Fabrice DUVAL
# import requests
from ast import operator
import os
import sys
# import random
import base64
# from pyquaternion import Quaternion

import commandeAPI

#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

position = {
    "poste1":{"x":35.78, "y":2.80, "theta":138.4, },
    "poste2":{"x":32.45, "y":-1.78, "theta":135.1, },
    "CNC":{"x":2.1, "y":-1.0, "theta":90.0, },
}
print(os.getcwd())
print(base64.b64decode(base64.b64encode(b"Base 64 Valide")))

def createRobot(factoryid, nom, typerobot, capacites, position2d=None, link=None):
    robot={}
    json = commandeAPI.createRobotResource(factoryid, nom, typerobot,capacites, position2d=position2d, link=link)
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
    nommap = "..\\Visualisation\\ceri3.png"
    scalemap = [(-20, -10, 0.0), 0.05] # position du point en bas à droite en coordonnée x, y, theta ; taille en m d'un pixel
    print(commandeAPI.urlTemplate)
    print(commandeAPI.urlTemplateFactory)
    nomfact = "Factory CERI"
    if Regeneration:
        # etape affacement de l'ancienne base
        listeinbase = commandeAPI.findfactory(name=nomfact)
        # listeinbase = findfactory(name="Factory LINEACT Test")
        effaceFactory = (len(listeinbase) != 1)  or Newfactoryid
        for usine in listeinbase:
            commandeAPI.deletepart(usine,typedata="resource")                           # database resource
            commandeAPI.deletepart(usine,typedata="product")                            # database product
            commandeAPI.deletepart(usine,typedata="taskMoveProductXFromStockAToStockB") # database task 1/3
            commandeAPI.deletepart(usine,typedata="taskProduce")                        # database task 2/3
            commandeAPI.deletepart(usine,typedata="taskHuman")                          # database task 3/3
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

        if renewmap:
            commandeAPI.mapinfactory(factoryid, nommap, scalemap[0], scalemap[1])

        ceriagv = createRobot(factoryid, "CERI_AGV", "ceriagv", [{"category": "transport"},{"category": "wait"}])
        ceriarm = createRobot(factoryid, "CERI_ARM", "ceriarm", [{"category": "grab"},{"category": "wait"}], position2d={"x":1.3, "y":0.0, "theta":0.0, }, link=ceriagv["robot"])
        cerirobot = commandeAPI.createMetaResource(factoryid, "CERI_META", "pickandmove", [ceriagv["robot"], ceriarm["robot"]])["_id"]
        cericncinout = commandeAPI.createStock(factoryid,"CNC_inout", "mixte", position2d={"x":2.0, "y":0.0, "theta":180.0}, typestock="stockMixte")
        cericncinout = cericncinout["_id"]
        cericncintern = commandeAPI.createStock(factoryid,"CNC_intern", "internal", typestock="stockMixte")
        cericncintern = cericncintern["_id"]
        cericnc = commandeAPI.createMachine(factoryid, "CERI_CNC", [cericncinout, cericncintern],
            [{'category':'production', 'capability':'machining'}, {'category':'production', 'capability':'empty'},
            {'category':'production', 'capability':'init'}],
            position=position["CNC"],)
        cericnc = cericnc["_id"]
        portecnc = commandeAPI.createMiscResource(factoryid, "PorteCNC")
        portecnc = portecnc["_id"] # resource à reserver pour action machine et chargement machine
        commandeAPI.updateobject(factoryid, "machine", cericnc, {"volume":{"dx":4.55, "dy":2.25, "dz":3.0, }})

        commandeAPI.updateobject(factoryid, "stock", cericncinout, {"link":cericnc})
        commandeAPI.updateobject(factoryid, "stock", cericncintern, {"link":cericnc})
        # updateRobotPoseRandom(factoryid, ceriagv["robot"])

        json = commandeAPI.createStock(factoryid, "Stockinitial", "mixte", position2d=position["poste1"])
        stockin = json["_id"]
        json = commandeAPI.createStock(factoryid, "StockIntermediate", "mixte", position2d=position["poste2"])
        stockflip = json["_id"]
        
        json = commandeAPI.createHumanResource(factoryid, "Operateur", "operator", [{"category": "transport"},{"category": "wait"},{"category": "grab"},{"category": "flip"}])
        human = json["_id"]


    else:
        factoryid = commandeAPI.findfactory(name=nomfact)[0]
        if renewmap:
            commandeAPI.mapinfactory(factoryid, nommap, scalemap[0], scalemap[1])

    print("done")
