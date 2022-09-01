# coding: utf8
# Copyright 2020 Fabrice DUVAL
# import requests
# import os
import sys
# import math
# import time
# import random
from pyquaternion import Quaternion
import Simulateurs.SimuMachineThreaded as simuMachine
import commandeAPI

Angle=Quaternion(axis=[0.0, 1.0, 0.0], degrees=90) #de l'axe Z à l'axe X

#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")


position = {
    "poste1":{"x":36.25, "y":2.09, "theta":138.4, },
    "poste2":{"x":33.00, "y":-2.40, "theta":135.1, },
    "poste3":{"x":16.44, "y":-5.0, "theta":180.0, },
    "poste4":{"x":15.00, "y":3.50, "theta":6.29, },
    "input":{"x":3.31, "y":-3.43, "theta":0.11, },
    "output":{"x":43.19, "y":23.15, "theta":-91.35, },
    # "output":{"x":40.66, "y":5.90, "theta":30.44, },
}

def getposte(factoryid, nomposte):
    retour = {}
    retour["poste"] = commandeAPI.findINfactory(factoryid, "machine", name=nomposte)[0]
    retour["in"] = commandeAPI.findINfactory(factoryid, "stock", name=nomposte+" in")[0]
    retour["out"] = commandeAPI.findINfactory(factoryid, "stock", name=nomposte+" out")[0]
    return retour

if __name__ == "__main__":
    Regeneration = True
    NettoyageOnly = False
    SimuMachine = False
    print(commandeAPI.urlTemplate)
    print(commandeAPI.urlTemplateFactory)
    nomfact = "Factory LINEACT Virtual"
    factoryid = commandeAPI.findfactory(name=nomfact)[0]
    robotbase = commandeAPI.findINfactory(factoryid, "robot", name="mir100_Arm")[0]
    if Regeneration:
        # etape affacement des anciennes commandes et poste virtuelle
        # deletepart(factoryid,typedata="resource")                           # on garde les resources
        commandeAPI.deletepart(factoryid,typedata="product")                            # database product
        commandeAPI.deletepart(factoryid,typedata="taskMoveProductXFromStockAToStockB") # database task 1/1
        commandeAPI.deletepart(factoryid,typedata="operation")                          # database operation
        commandeAPI.deletepart(factoryid,typedata="job")                                # database job
        commandeAPI.deletepart(factoryid,typedata="jobdescription")                     # database jobdescription
        commandeAPI.deletepart(factoryid,typedata="order")                              # database order
    
    if NettoyageOnly:
        quit()

    json = commandeAPI.createProduct(factoryid, "cesi-corot RAWPART 1", "fourniture poste 1")
    raw1 = json["_id"]
    json = commandeAPI.createProduct(factoryid, "cesi-corot RAWPART 2", "fourniture poste 2")
    raw2 = json["_id"]
    json = commandeAPI.createProduct(factoryid, "cesi-corot RAWPART 3", "fourniture poste 3")
    raw3 = json["_id"]
    json = commandeAPI.createProduct(factoryid, "cesi-corot RAWPART 4", "fourniture poste 4")
    raw4 = json["_id"]
    json = commandeAPI.createProduct(factoryid, "cesi-corot inter1-2", "fourniture poste 2 depuis 1")
    raw12 = json["_id"]
    json = commandeAPI.createProduct(factoryid, "cesi-corot inter2-4", "fourniture poste 4 depuis 2")
    raw24 = json["_id"]
    json = commandeAPI.createProduct(factoryid, "cesi-corot inter3-4", "fourniture poste 4 depuis 3")
    raw34 = json["_id"]
    json = commandeAPI.createProduct(factoryid, "cesi-corot Final", "produit final")
    produitout = json["_id"]

    stockappro = commandeAPI.findINfactory(factoryid, "stock", name="Stock Approvisionnement")[0]
    stockout = commandeAPI.findINfactory(factoryid, "stock", name="Stock sortie")[0]
    poste1 = getposte(factoryid, "Poste 1")
    poste2 = getposte(factoryid, "Poste 2")
    poste3 = getposte(factoryid, "Poste 3")
    poste4 = getposte(factoryid, "Poste 4")

    # operation corot P1-->P2-->P4<--P3
    operationsRobot = [""]*20
    # approvisionnement
    operationsRobot[1] = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0, 0, 0, stockappro),name="A_1")["_id"]# A
    operationsRobot[2] = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0, 0, 0, poste1["in"]),name="A_2", previous=operationsRobot[1])["_id"]
    commandeAPI.updateobject(factoryid, "operation", operationsRobot[1], {"nextOperationInfo":operationsRobot[2]})
    operationsRobot[3] = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0, 0, 0, stockappro),name="B_1")["_id"]# B
    operationsRobot[4] = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0, 0, 0, poste2["in"]),name="B_2", previous=operationsRobot[3])["_id"]
    commandeAPI.updateobject(factoryid, "operation", operationsRobot[3], {"nextOperationInfo":operationsRobot[4]})
    operationsRobot[5] = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0, 0, 0, stockappro),name="C_1")["_id"]# C
    operationsRobot[6] = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0, 0, 0, poste3["in"]),name="C_2", previous=operationsRobot[5])["_id"]
    commandeAPI.updateobject(factoryid, "operation", operationsRobot[5], {"nextOperationInfo":operationsRobot[6]})
    operationsRobot[7] = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0, 0, 0, stockappro),name="D_1")["_id"]# D
    operationsRobot[8] = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0, 0, 0, poste4["in"]),name="D_2", previous=operationsRobot[7])["_id"]
    commandeAPI.updateobject(factoryid, "operation", operationsRobot[7], {"nextOperationInfo":operationsRobot[8]})

    operationsRobot[9] = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0, 0, 0, poste1["out"]),name="E_1")["_id"]# E
    operationsRobot[10] = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0, 0, 0, poste2["in"]),name="E_2", previous=operationsRobot[9])["_id"]
    commandeAPI.updateobject(factoryid, "operation", operationsRobot[9], {"nextOperationInfo":operationsRobot[10]})
    operationsRobot[11] = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0, 0, 0, poste2["out"]),name="F_1")["_id"]# F
    operationsRobot[12] = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0, 0, 0, poste4["in"]),name="F_2", previous=operationsRobot[11])["_id"]
    commandeAPI.updateobject(factoryid, "operation", operationsRobot[11], {"nextOperationInfo":operationsRobot[12]})
    operationsRobot[13] = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0, 0, 0, poste3["out"]),name="G_1")["_id"]# G
    operationsRobot[14] = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0, 0, 0, poste4["in"]),name="G_2", previous=operationsRobot[13])["_id"]
    commandeAPI.updateobject(factoryid, "operation", operationsRobot[13], {"nextOperationInfo":operationsRobot[14]})
    operationsRobot[15] = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0, 0, 0, poste4["out"]),name="H_1")["_id"]# H
    operationsRobot[16] = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0, 0, 0, stockout),name="H_2", previous=operationsRobot[15])["_id"]
    commandeAPI.updateobject(factoryid, "operation", operationsRobot[15], {"nextOperationInfo":operationsRobot[16]})

    # creation des taches machines
    operationMachine=[""]*5
    operationMachine[1] = commandeAPI.createOperationMachine(factoryid, poste1["poste"], name="Machine 1", previous=operationsRobot[2])["_id"]
    operationMachine[2] = commandeAPI.createOperationMachine(factoryid, poste2["poste"], name="Machine 2", previous=[operationsRobot[4],operationsRobot[10],])["_id"]
    operationMachine[3] = commandeAPI.createOperationMachine(factoryid, poste3["poste"], name="Machine 3", previous=operationsRobot[6])["_id"]
    operationMachine[4] = commandeAPI.createOperationMachine(factoryid, poste4["poste"], name="Machine 4", previous=[operationsRobot[8],operationsRobot[12],operationsRobot[14],])["_id"]

    commandeAPI.updateobject(factoryid, "operation", operationsRobot[9], {"precedenceOperationInfo":commandeAPI.formalize2list(operationMachine[1])}) # operation E si poste 1 fini
    commandeAPI.updateobject(factoryid, "operation", operationsRobot[11], {"precedenceOperationInfo":commandeAPI.formalize2list(operationMachine[2])})# operation F si poste 2 fini
    commandeAPI.updateobject(factoryid, "operation", operationsRobot[13], {"precedenceOperationInfo":commandeAPI.formalize2list(operationMachine[3])})# operation G si poste 3 fini
    commandeAPI.updateobject(factoryid, "operation", operationsRobot[15], {"precedenceOperationInfo":commandeAPI.formalize2list(operationMachine[4])})# operation H si poste 4 fini

    # on valide toutes les opération
    for num in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, ]:
        commandeAPI.updatestatus(factoryid, "operation", operationsRobot[num], "toDo")
    for num in [1, 2, 3, 4, ]:
        commandeAPI.updatestatus(factoryid, "operation", operationMachine[num], "toDo")

    print("done")
