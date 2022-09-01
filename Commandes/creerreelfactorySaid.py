# coding: utf8
# Copyright 2020 Fabrice DUVAL
# import requests
import os
import sys
import math
# import random
import base64
# from pyquaternion import Quaternion

import commandeAPI

import threading


#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()
print(os.getcwd())
print(base64.b64decode(base64.b64encode(b"Base 64 Valide")))

try:
    #print("API in remote mode: ",sys.argv[1])
    #commandeAPI.seturl(sys.argv[1])
    commandeAPI.seturl("http://robigdata.rorecherche:5000/")
except IndexError:
    print("API in local 127.0.0.1")

position = {
    "poste1":{"x":3.45, "y":9.51, "theta":180.0, },
    "poste2":{"x":7.42, "y":9.70, "theta":0.0, },
    "stock1":{"x":4.41, "y":3.66, "theta":180.0, },
    "stock2":{"x":9.31, "y":8.83, "theta":90.0, },
    # "output":{"x":40.66, "y":5.90, "theta":30.44, },
}

def createRobot(factoryid, nom, typerobot, capacites):
    robot={}
    json = commandeAPI.createRobotResource(factoryid, nom, typerobot,capacites)
    robot["robot"] = json["_id"]
    json = commandeAPI.createStock(factoryid, nom + " in", "in", link=robot["robot"])
    robot["in"] = json["_id"]
    json = commandeAPI.createStock(factoryid, nom + " out", "out", link=robot["robot"])
    robot["out"] = json["_id"]
    return robot

def createPosteSaid(factoryid, nom, position, link=None ):
    """création d'un poste constitué d'une machine de tailleposte=[x,y,z]
    associé à une zone de stockage de taillerobot en entré et en sortie
    a la position du stock (la machine est décalée en conséquence
    le nez du robot est placé face au coté 'x'
    retourne [idmachine, idstockin, idstockout]"""
    # taille poste 1.0 * 1.0 * 0.8
    # taille robot 1.0 * 0.6 * 0.4
    xmachine = position["x"]
    ymachine = position["y"]
    tmachine = position["theta"] * math.pi / 180
    ecartcentre = 1.05 #taille inter robot - machine
    xrobotin = xmachine - ecartcentre * math.sin(tmachine)
    yrobotin = ymachine + ecartcentre * math.cos(tmachine)
    xrobotout = xmachine + ecartcentre * math.sin(tmachine)
    yrobotout = ymachine - ecartcentre * math.cos(tmachine)

    poste={}
    json = commandeAPI.createMachine(factoryid, nom, [], [{"category": "production"},], position={"x":xmachine, "y":ymachine, "theta":position["theta"], }, link=link)
    poste["poste"] = json["_id"]

    commandeAPI.updateobject(factoryid,"machine",poste["poste"],{"volume":{"dx":1.0, "dy":1.0, "dz":0.8}})
    json = commandeAPI.createStock(factoryid, nom + " in", "in", position2d={"x":0.0, "y":+ecartcentre, "theta":0.0, }, link=poste["poste"])
    poste["in"] = json["_id"]
    json = commandeAPI.createStock(factoryid, nom + " out", "out", position2d={"x":0.0, "y":-ecartcentre, "theta":180.0, }, link=poste["poste"])
    poste["out"] = json["_id"]
    return poste

if __name__ == "__main__":
    Regeneration = True
    Newfactoryid = True
    NewRobotid = True
    renewmap = True
    nommap = "..\\Visualisation\\MadrilletSaid.png"
    scalemap = [(-20.5, -34.2, 0.0), 0.05]
    print(commandeAPI.urlTemplate)
    print(commandeAPI.urlTemplateFactory)
    nomfact = "Factory Said"
    if Regeneration:
        # etape affacement de l'ancienne base
        listeinbase = commandeAPI.findfactory(name=nomfact)
        # listeinbase = findfactory(name="Factory LINEACT Test")
        effaceFactory = (len(listeinbase) != 1)  or Newfactoryid
        for usine in listeinbase:
            if NewRobotid or effaceFactory:
                commandeAPI.deletepart(usine,typedata="resource")                           # database resource
            else:
                commandeAPI.deletepart(usine,typedata="human")                           # database resource
            commandeAPI.deletepart(usine,typedata="product")                            # database product
            commandeAPI.deletepart(usine,typedata="taskMoveProductXFromStockAToStockB") # database task 1/1
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
        if NewRobotid:
            mir100 = createRobot(factoryid, "mir100_Arm", "mir100", [{"category": "transport"},{"category": "wait"}])
            ur10 = createRobot(factoryid, "ur10_1", "ur10", [{"category": "grab"},{"category": "wait"}])
        else:
            mir100={}
            mir100["robot"] = commandeAPI.findINfactory(factoryid, "robot", name="mir100_Arm")[0]
            ur10={}
            ur10["robot"] = commandeAPI.findINfactory(factoryid, "robot", name="ur10_1")[0]            


        # commandeAPI.updateRobotPoseRandom(factoryid, mir100["robot"])
        # commandeAPI.updateRobotPoseRandom(factoryid, ur10["robot"])


        json = commandeAPI.createHumanResource(factoryid, "Operator_01", "operator" , [{"category": "transport"},{"category": "wait"},{"category": "grab"}])
        Operator_01 = json["_id"]
        json = commandeAPI.createHumanResource(factoryid, "Operator_02", "operator", [{"category": "transport"},{"category": "wait"},{"category": "grab"}])
        Operator_02 = json["_id"]
        json = commandeAPI.createHumanResource(factoryid, "Operator_03", "operator" , [{"category": "transport"},{"category": "wait"},{"category": "grab"}])
        Operator_03 = json["_id"]
        json = commandeAPI.createHumanResource(factoryid, "Operator_04", "operator", [{"category": "transport"},{"category": "wait"},{"category": "grab"}])
        Operator_04 = json["_id"]

        #Create Machines

        poste1 = createPosteSaid(factoryid, "Poste 1", position["poste1"])
        poste2 = createPosteSaid(factoryid, "Poste 2", position["poste2"])
        
        json = commandeAPI.createStock(factoryid, "Stock Approvisionnement", "out", position2d=position["stock1"])
        stockappro = json["_id"]
        json = commandeAPI.createStock(factoryid, "Stock sortie", "in", position2d=position["stock2"])
        stockout = json["_id"]

        print("Done creating resources")


        poste1={}
        poste1["poste"] = commandeAPI.findINfactory(factoryid, "machine", name="Poste 1")[0]
        poste1["in"] = commandeAPI.findINfactory(factoryid, "stock", name="Poste 1 in")[0]
        poste1["out"] = commandeAPI.findINfactory(factoryid, "stock", name="Poste 1 out")[0]
        poste2={}
        poste2["poste"] = commandeAPI.findINfactory(factoryid, "machine", name="Poste 2")[0]
        poste2["in"] = commandeAPI.findINfactory(factoryid, "stock", name="Poste 2 in")[0]
        poste2["out"] = commandeAPI.findINfactory(factoryid, "stock", name="Poste 2 out")[0]


        #create operations
        m11 = commandeAPI.createOperationMoveRobotTo(factoryid, mir100["robot"], (0, 0, 0, stockappro), name="m11")["_id"]

        o11 = commandeAPI.createOperationHuman(factoryid, Operator_01, (0, 0, 0, stockappro), ["charger le mir"], name="o11", previous=m11)["_id"]

        m12 = commandeAPI.createOperationMoveRobotTo(factoryid, mir100["robot"], (0, 0, 0, poste1["in"]), name="m12", previous=o11)["_id"]
        commandeAPI.updateobject(factoryid, "operation", m11, {"nextOperationInfo":m12})

        p11 = commandeAPI.createOperationHuman(factoryid, Operator_02, (0, 0, 0, poste1["in"]), ["decharger le mir"], name="p11", previous=m12)["_id"]

        m21 = commandeAPI.createOperationMoveRobotTo(factoryid, mir100["robot"], (0, 0, 0, poste1["out"]), name="m21", previous=p11)["_id"]
        # commandeAPI.updateobject(factoryid, "operation", m12, {"nextOperationInfo":m21})

        p12 = commandeAPI.createOperationMachine(factoryid, poste1["poste"], name="p12", previous=p11)["_id"]
        commandeAPI.updateobject(factoryid, "operation", p12, {"precedenceOperationInfo":commandeAPI.formalize2list(p11)}) # operation E si poste 1 fini
    
        p13 = commandeAPI.createOperationHuman(factoryid, Operator_02, (0, 0, 0, poste1["out"]), ["charger le mir"], name="p13", previous=[p12,m21,])["_id"]
        commandeAPI.updateobject(factoryid, "operation", p13, {"precedenceOperationInfo":commandeAPI.formalize2list([p12,m21])}) # operation E si poste 1 fini

        m22 = commandeAPI.createOperationMoveRobotTo(factoryid, mir100["robot"], (0, 0, 0, poste2["in"]), name="m22", previous=p13)["_id"]
        commandeAPI.updateobject(factoryid, "operation", m21, {"nextOperationInfo":m22})
        
        p21 = commandeAPI.createOperationHuman(factoryid, Operator_03, (0, 0, 0, poste2["in"]), ["decharger le mir"], name="p21", previous=m22)["_id"]

        m31 = commandeAPI.createOperationMoveRobotTo(factoryid, mir100["robot"], (0, 0, 0, poste2["out"]), name="m31", previous=p21)["_id"]
        # commandeAPI.updateobject(factoryid, "operation", m22, {"nextOperationInfo":m31})

        p22 = commandeAPI.createOperationMachine(factoryid, poste1["poste"], name="p22", previous=p21)["_id"]
        commandeAPI.updateobject(factoryid, "operation", p22, {"precedenceOperationInfo":commandeAPI.formalize2list(p21)}) # operation E si poste 1 fini
    
        p23 = commandeAPI.createOperationHuman(factoryid, Operator_03, (0, 0, 0, poste2["out"]), ["charger le mir"], name="p23", previous=[p22,m31,])["_id"]
        commandeAPI.updateobject(factoryid, "operation", p23, {"precedenceOperationInfo":commandeAPI.formalize2list([p22,m31])})
        
        m32 = commandeAPI.createOperationMoveRobotTo(factoryid, mir100["robot"], (0, 0, 0, stockout), name="m32", previous=p23)["_id"]
        commandeAPI.updateobject(factoryid, "operation", m31, {"nextOperationInfo":m32})

        o12 = commandeAPI.createOperationHuman(factoryid, Operator_04, (0, 0, 0, stockout), ["decharger le mir"], name="o12", previous=m32)["_id"]
        
        print("Done creating operations")



    else:
        factoryid = commandeAPI.findfactory(name=nomfact)[0]
        mir100={}
        mir100["robot"] = commandeAPI.findINfactory(factoryid, "robot", name="mir100_Arm")[0]
        ur10={}
        ur10["robot"] = commandeAPI.findINfactory(factoryid, "robot", name="ur10_1")[0]
        poste1={}
        poste1["poste"] = commandeAPI.findINfactory(factoryid, "machine", name="Poste 1")[0]
        poste1["in"] = commandeAPI.findINfactory(factoryid, "stock", name="Poste 1 in")[0]
        poste1["out"] = commandeAPI.findINfactory(factoryid, "stock", name="Poste 1 out")[0]
        poste2={}
        poste2["poste"] = commandeAPI.findINfactory(factoryid, "machine", name="Poste 2")[0]
        poste2["in"] = commandeAPI.findINfactory(factoryid, "stock", name="Poste 2 in")[0]
        poste2["out"] = commandeAPI.findINfactory(factoryid, "stock", name="Poste 2 out")[0]
        if renewmap:
            commandeAPI.mapinfactory(factoryid, nommap, scalemap[0], scalemap[1])

    print("done")

