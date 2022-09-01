# coding: utf8
# Copyright 2020 Fabrice DUVAL
# import requests
# import os
# import math
import time
import sys
# import random
# import Simulateurs.SimuMachineThreaded as simuMachine
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
    print(commandeAPI.urlTemplate)
    print(commandeAPI.urlTemplateFactory)
    nomfact = "Factory CERI"
    nommachine = "CERI_CNC"
    nomporte = "PorteCNC"
    nomAGV = "CERI_AGV"
    nomARM = "CERI_ARM"
    nomMETA = "CERI_META"
    nomOperator = "Operateur"
    stock1 = "Stockinitial"
    stock2 = "StockIntermediate"

    factoryid = commandeAPI.findfactory(name=nomfact)[0]
    if Regeneration:
        # etape affacement des anciennes commandes et poste virtuelle
        # deletepart(factoryid,typedata="resource")                           # on garde les resources
        # commandeAPI.deletepart(factoryid,typedata="resource")                           # database resource
        commandeAPI.deletepart(factoryid,typedata="product")                            # database product
        # commandeAPI.deletepart(factoryid,typedata="stock")
        commandeAPI.deletepart(factoryid,typedata="taskMoveProductXFromStockAToStockB") # database task 1/3
        commandeAPI.deletepart(factoryid,typedata="taskHuman")                          # database task 2/3
        commandeAPI.deletepart(factoryid,typedata="taskProduce")                        # database task 3/3
        commandeAPI.deletepart(factoryid,typedata="operation")                          # database operation
        commandeAPI.deletepart(factoryid,typedata="job")                                # database job
        commandeAPI.deletepart(factoryid,typedata="jobdescription")                     # database jobdescription
        commandeAPI.deletepart(factoryid,typedata="order")                              # database order
        # commandeAPI.deletepart(factoryid,typedata="machine")                            # database machine
        if NettoyageOnly:
            quit()

    json = commandeAPI.createProduct(factoryid, "Raw_Part N_1", "Raw_Part")
    productid = json["_id"]
    commandeAPI.updateobject(factoryid, "product", productid, {"operationToDoList":[{"operation":"CNC", "status":"toDo", "parameters":["Face1"]},{"operation":"CNC", "status":"toDo", "parameters":["Face2"]}]})
    product = commandeAPI.getvalues(factoryid, "product", productid)

    machineid = commandeAPI.findINfactory(factoryid, "machine", name=nommachine)[0]
    portemachine = commandeAPI.findINfactory(factoryid, "resource", name=nomporte)[0]
    commandeAPI.updateobject(factoryid, "resource", portemachine, {"status":"free", "internalParams": {"reservedby": ""},})
    AGVid = commandeAPI.findINfactory(factoryid, "robot", name=nomAGV)[0]
    ARMid = commandeAPI.findINfactory(factoryid, "robot", name=nomARM)[0]
    METAid = commandeAPI.findINfactory(factoryid, "meta", name=nomMETA)[0]
    Opeid = commandeAPI.findINfactory(factoryid, "human", name=nomOperator)[0]
    Stock1id = commandeAPI.findINfactory(factoryid, "stock", name=stock1)[0]
    Stock2id = commandeAPI.findINfactory(factoryid, "stock", name=stock2)[0]


    machine = commandeAPI.getvalues(factoryid, "machine", machineid)
    stockid = machine["stockList"][0]
    stock = commandeAPI.getvalues(factoryid, "stock", stockid)
    if stock["mode"] == "internal":
        stockinterneid = stockid
        stockinterne = stock
        stockinoutid = machine["stockList"][1]
        stockinout = commandeAPI.getvalues(factoryid, "stock", stockinoutid)
    else:
        stockinoutid = stockid
        stockinout = stock
        stockinterneid = machine["stockList"][1]
        stockinterne = commandeAPI.getvalues(factoryid, "stock", stockinterneid)

    # on pose un objet dans la stock d'entree
    commandeAPI.updateobject(factoryid, "product", productid, {"link":Stock1id})

    #create task list
    tasklist = []
    tasklist.append(commandeAPI.createTaskMoveProductXFromAToB(factoryid, "Tache A", productid, stockAId=Stock1id, stockBId=stockinoutid, resource=METAid)["_id"])
    tasklist.append(commandeAPI.createTaskProduce(factoryid,"Tache B","Produce","Intermediate_Part N_1",[],productid, resource=machineid, precedence=tasklist[-1])["_id"])
    tasklist.append(commandeAPI.createTaskMoveProductXFromAToB(factoryid, "Tache C", productid, stockAId=stockinoutid, stockBId=Stock2id, resource=METAid, precedence=tasklist[-1])["_id"])
    tasklist.append(commandeAPI.createTaskHuman(factoryid,"Tache D","Retournement","R_Intermediate_Part N_1",[],productid,["retourner la piece","fixer la piece"], position=(0,0,0,Stock2id), resource=Opeid, precedence=tasklist[-1])["_id"])
    tasklist.append(commandeAPI.createTaskMoveProductXFromAToB(factoryid, "Tache E", productid, stockAId=Stock2id, stockBId=stockinoutid, resource=METAid, precedence=tasklist[-1])["_id"])
    tasklist.append(commandeAPI.createTaskProduce(factoryid,"Tache F","Produce","Near Final Part N_1",[],productid, resource=machineid, precedence=tasklist[-1])["_id"])
    tasklist.append(commandeAPI.createTaskMoveProductXFromAToB(factoryid, "Tache G", productid, stockAId=stockinoutid, stockBId=Stock2id, resource=METAid, precedence=tasklist[-1])["_id"])
    tasklist.append(commandeAPI.createTaskHuman(factoryid,"Tache H","Demontage","Final Part N_1",[],productid,["retourner la piece","demonter le socle","reposer la piece"], position=(0,0,0,Stock2id), resource=Opeid, precedence=tasklist[-1])["_id"])
    tasklist.append(commandeAPI.createTaskMoveProductXFromAToB(factoryid, "Tache I", productid, stockAId=Stock2id, stockBId=Stock1id, resource=METAid, precedence=tasklist[-1])["_id"])



    # # create operation list
    # operationlist = []
    # operationlist.append(commandeAPI.createOperationMoveRobotTo(factoryid, AGVid, (0, 0, 0, Stock1id),name="A_1")["_id"])# A
    # operationlist.append(commandeAPI.createOperationGrab(factoryid, ARMid, [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="frominit", name="A_2", previous=operationlist[-1])["_id"])# A
    # operationlist.append(commandeAPI.createOperationMoveRobotTo(factoryid, AGVid, (0, 0, 0, stockinoutid),name="A_3", previous=operationlist[-1])["_id"])# A
    # commandeAPI.updateobject(factoryid, "operation", operationlist[-2], {"nextOperationInfo":operationlist[-1]})
    # operationlist.append(commandeAPI.createOperationGrab(factoryid, ARMid, [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="toCNC", name="A_2", previous=operationlist[-1])["_id"])# A

    # operationlist.append(commandeAPI.createOperationMachine(factoryid, machineid, name="B", previous=operationlist[-1])["_id"])

    # operationlist.append(commandeAPI.createOperationMoveRobotTo(factoryid, AGVid, (0, 0, 0, stockinoutid),name="C_1", previous=operationlist[-1])["_id"])
    # operationlist.append(commandeAPI.createOperationGrab(factoryid, ARMid, [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="fromCNC", name="C_2", previous=operationlist[-1])["_id"])
    # operationlist.append(commandeAPI.createOperationMoveRobotTo(factoryid, AGVid, (0, 0, 0, Stock2id),name="C_3", previous=operationlist[-1])["_id"])
    # commandeAPI.updateobject(factoryid, "operation", operationlist[-2], {"nextOperationInfo":operationlist[-1]})
    # operationlist.append(commandeAPI.createOperationGrab(factoryid, ARMid, [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="putflip", name="C_4", previous=operationlist[-1])["_id"])# A

    # operationlist.append(commandeAPI.createOperationHuman(factoryid, Opeid, (0, 0, 0, Stock2id), ["retourner la plaque"], name="D", previous=operationlist[-1])["_id"])

    # operationlist.append(commandeAPI.createOperationMoveRobotTo(factoryid, AGVid, (0, 0, 0, Stock2id),name="E_1", previous=operationlist[-1])["_id"])
    # operationlist.append(commandeAPI.createOperationGrab(factoryid, ARMid, [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="fromflip", name="E_2", previous=operationlist[-1])["_id"])
    # operationlist.append(commandeAPI.createOperationMoveRobotTo(factoryid, AGVid, (0, 0, 0, stockinoutid),name="E_3", previous=operationlist[-1])["_id"])
    # commandeAPI.updateobject(factoryid, "operation", operationlist[-2], {"nextOperationInfo":operationlist[-1]})
    # operationlist.append(commandeAPI.createOperationGrab(factoryid, ARMid, [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="toCNC", name="E_E", previous=operationlist[-1])["_id"])# A

    # operationlist.append(commandeAPI.createOperationMachine(factoryid, machineid, name="F", previous=operationlist[-1])["_id"])

    # operationlist.append(commandeAPI.createOperationMoveRobotTo(factoryid, AGVid, (0, 0, 0, stockinoutid),name="G_1", previous=operationlist[-1])["_id"])
    # operationlist.append(commandeAPI.createOperationGrab(factoryid, ARMid, [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="fromCNC", name="G_2", previous=operationlist[-1])["_id"])
    # operationlist.append(commandeAPI.createOperationMoveRobotTo(factoryid, AGVid, (0, 0, 0, Stock2id),name="G_3", previous=operationlist[-1])["_id"])
    # commandeAPI.updateobject(factoryid, "operation", operationlist[-2], {"nextOperationInfo":operationlist[-1]})
    # operationlist.append(commandeAPI.createOperationGrab(factoryid, ARMid, [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="putflip2", name="A_2", previous=operationlist[-1])["_id"])# A

    # operationlist.append(commandeAPI.createOperationHuman(factoryid, Opeid, (0, 0, 0, Stock2id), ["Enlever les supports plaque"], name="H", previous=operationlist[-1])["_id"])

    # operationlist.append(commandeAPI.createOperationMoveRobotTo(factoryid, AGVid, (0, 0, 0, Stock2id),name="I_1", previous=operationlist[-1])["_id"])
    # operationlist.append(commandeAPI.createOperationGrab(factoryid, ARMid, [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="fromflip2", name="I_2", previous=operationlist[-1])["_id"])
    # operationlist.append(commandeAPI.createOperationMoveRobotTo(factoryid, AGVid, (0, 0, 0, Stock1id),name="I_3", previous=operationlist[-1])["_id"])
    # commandeAPI.updateobject(factoryid, "operation", operationlist[-2], {"nextOperationInfo":operationlist[-1]})
    # operationlist.append(commandeAPI.createOperationGrab(factoryid, ARMid, [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="toinit", name="E_E", previous=operationlist[-1])["_id"])# A

    # on valide toutes les opération
    # for num in range(len(operationlist)):
    #     commandeAPI.updatestatus(factoryid, "operation", operationlist[num], "toDo")
    # on valide toutes les taches
    for num in range(len(tasklist)):
        commandeAPI.updatestatus(factoryid, "task", tasklist[num], "toDo")

    print("done 3")
    