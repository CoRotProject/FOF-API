# coding: utf8
# Copyright 2020 Fabrice DUVAL
# import requests
# import os
# import math
import time
import sys
# import random
from pyquaternion import Quaternion
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

Angle=Quaternion(axis=[0.0, 1.0, 0.0], degrees=90) #de l'axe Z à l'axe X

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
    factoryid = commandeAPI.findfactory(name=nomfact)[0]
    if Regeneration:
        # etape affacement des anciennes commandes et poste virtuelle
        # deletepart(factoryid,typedata="resource")                           # on garde les resources
        # commandeAPI.deletepart(factoryid,typedata="resource")                           # database resource
        commandeAPI.deletepart(factoryid,typedata="product")                            # database product
        # commandeAPI.deletepart(factoryid,typedata="stock")
        commandeAPI.deletepart(factoryid,typedata="taskMoveProductXFromStockAToStockB") # database task 1/1
        commandeAPI.deletepart(factoryid,typedata="operation")                          # database operation
        commandeAPI.deletepart(factoryid,typedata="job")                                # database job
        commandeAPI.deletepart(factoryid,typedata="jobdescription")                     # database jobdescription
        commandeAPI.deletepart(factoryid,typedata="order")                              # database order
        # commandeAPI.deletepart(factoryid,typedata="machine")                            # database machine
        if NettoyageOnly:
            quit()

    json = commandeAPI.createProduct(factoryid, "Raw_Part N_1", "Raw_Par")
    productid = json["_id"]
    commandeAPI.updateobject(factoryid, "product", productid, {"operationToDoList":[{"operation":"CNC", "status":"toDo"}]})
    product = commandeAPI.getvalues(factoryid, "product", productid)

    machineid = commandeAPI.findINfactory(factoryid, "machine", name=nommachine)[0]
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
    
    # on pose un objet dans la machine
    commandeAPI.updateobject(factoryid, "product", productid, {"link":stockinoutid})
    # On cree une action machine 

    operationMachine = commandeAPI.createOperationMachine(factoryid, machineid, name="produce 1")["_id"]
    commandeAPI.updatestatus(factoryid, "operation", operationMachine, "toDo")
    print("done 1")
    while not commandeAPI.getstatus(factoryid, "operation", operationMachine) == "done":
        time.sleep(3.0)
        print("wait end")

    # Create new product
    json = commandeAPI.createProduct(factoryid, "Raw_Part N_2", "Raw_Par")
    productid = json["_id"]
    commandeAPI.updateobject(factoryid, "product", productid, {"operationToDoList":[{"operation":"CNC", "status":"toDo"}]})
    # on pose un objet dans la machine
    commandeAPI.updateobject(factoryid, "product", productid, {"link":stockinoutid})

    operationMachine = commandeAPI.createOperationMachine(factoryid, machineid, name="produce 2")["_id"]
    commandeAPI.updatestatus(factoryid, "operation", operationMachine, "toDo")
    print("done 2")
    # try to create error mission
    while not commandeAPI.getstatus(factoryid, "operation", operationMachine) == "done":
        time.sleep(3.0)
        print("wait end")

    operationMachine = commandeAPI.createOperationMachine(factoryid, machineid, name="produce 3")["_id"]
    commandeAPI.updatestatus(factoryid, "operation", operationMachine, "toDo")
    print("done 3")
    