# coding: utf8
# Copyright 2020 Fabrice DUVAL
# import requests
import sys
# import random
from pyquaternion import Quaternion

import commandeAPI

#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

def testmove():
    factoryid = commandeAPI.findfactory(name="Factory LINEACT Test Fabrice")[0]
    mir100Id1 = commandeAPI.findINfactory(factoryid, "robot", name="mir100_Arm")[0]
    mir100Id2 = commandeAPI.findINfactory(factoryid, "robot", name="mir100_Capitaine")[0]
    a1 = commandeAPI.createOperationMoveRobotTo(factoryid, mir100Id1, (0, 0, 0))["_id"]
    a2 = commandeAPI.createOperationMoveRobotTo(factoryid, mir100Id1, (12, 12, 45),previous=a1)["_id"]
    a3 = commandeAPI.createOperationMoveRobotTo(factoryid, mir100Id1, (12, 0, 78),previous=a1)["_id"]
    a4 = commandeAPI.createOperationMoveRobotTo(factoryid, mir100Id1, (0, 12, 156),previous=a1)["_id"]
    commandeAPI.updateobject(factoryid, "operation", a4, {"nextOperationInfo":a1})
    a5 = commandeAPI.createOperationMoveRobotTo(factoryid, mir100Id2, (6, 6, 90))["_id"]
    a6 = commandeAPI.createOperationMoveRobotTo(factoryid, mir100Id2, (-1, 6, 0),previous=a5)["_id"]
    a7 = commandeAPI.createOperationMoveRobotTo(factoryid, mir100Id2, (5, 8, 45),previous=a6)["_id"]
    a8 = commandeAPI.createOperationMoveRobotTo(factoryid, mir100Id2, (9, 4, 135),previous=a7)["_id"]
    a9 = commandeAPI.createOperationMoveRobotTo(factoryid, mir100Id2, (0, 0, 15),previous=a8)["_id"]
    for operation in commandeAPI.findINfactory(factoryid, "operation", status="standBy"):
        commandeAPI.updatestatus(factoryid, "operation", operation, "toDo")


if __name__ == "__main__":
    Regeneration = True
    NewFactoryId = False
    print(commandeAPI.urlTemplate)
    print(commandeAPI.urlTemplateFactory)
    if Regeneration:
        # etape affacement de l'ancienne base
        listeinbase = commandeAPI.findfactory(name="Factory LINEACT Test Fabrice")
        effaceFactory = (len(listeinbase) != 1)  or NewFactoryId
        for usine in listeinbase:
            commandeAPI.deletepart(usine,typedata="resource")                           # database resource
            commandeAPI.deletepart(usine,typedata="product")                            # database product
            commandeAPI.deletepart(usine,typedata="taskMoveProductXFromStockAToStockB") # database task 1/1
            commandeAPI.deletepart(usine,typedata="stock")                              # database stock
            commandeAPI.deletepart(usine,typedata="operation")                          # database operation
            commandeAPI.deletepart(usine,typedata="job")                                # database job
            commandeAPI.deletepart(usine,typedata="jobdescription")                     # database jobdescription
            commandeAPI.deletepart(usine,typedata="order")                              # database order
            if effaceFactory:
                commandeAPI.deletepart(usine)
        if effaceFactory:
            json = commandeAPI.createFactory("Factory LINEACT Test Fabrice")
            factoryId = json["_id"]
        else:
            factoryId = usine
        json = commandeAPI.createRobotResource(factoryId, "mir100_Arm", "mir100",[{"category": "transport"},{"category": "wait"}])
        mir100Id = json["_id"]
        json = commandeAPI.createRobotResource(factoryId, "mir100_Capitaine", "mir100",[{"category": "transport"},{"category": "wait"}])
        mir100CapitaineId = json["_id"]
        json = commandeAPI.createRobotResource(factoryId, "ur10_1", "ur10", [{"category": "grab"},{"category": "wait"}])
        ur10Id = json["_id"]
        json = commandeAPI.createRobotResource(factoryId, "ur5_1", "ur5", [{"category": "grab"},{"category": "wait"}])
        ur5Id = json["_id"]
        json = commandeAPI.getvalues(factoryId,"resource",ur5Id)
        ur5test = json["_id"]
        commandeAPI.updateRobotPoseRandom(factoryId, mir100Id)
        commandeAPI.updateRobotPoseRandom(factoryId, ur10Id)
        commandeAPI.updateRobotPoseRandom(factoryId, ur5Id)
        json = commandeAPI.createHumanResource(factoryId, "Michel", "operator", [{"category": "transport"},{"category": "wait"},{"category": "grab"}])
        Michel = json["_id"]
        json = commandeAPI.createHumanResource(factoryId, "Fabrice", "operator" , [{"category": "transport"},{"category": "wait"},{"category": "grab"}])
        Fabrice = json["_id"]
        json = commandeAPI.createHumanResource(factoryId, "M'hammed", "operator", [{"category": "transport"},{"category": "wait"},{"category": "grab"}])
        Mhammed = json["_id"]
        json = commandeAPI.createStock(factoryId, "Stock A", "out")
        stockAId = json["_id"]
        json = commandeAPI.createStock(factoryId, "Stock B", "in")
        stockBId = json["_id"]
        json = commandeAPI.createProduct(factoryId, "Samsung A5 - S/N 1234567890", "Samsung A5")
        productId = json["_id"]
        json = commandeAPI.createProduct(factoryId, "Samsung S7 - S/N ABCDEFGHIJ", "Samsung S7")
        productId2 = json["_id"]
        json = commandeAPI.createProduct(factoryId, "iPhone 10 Custom", "Samsung S7")
        productId3 = json["_id"]
        json = commandeAPI.createTaskMoveProductXFromStockAToStockB(factoryId, "Move Task", productId, stockAId, stockBId)
        taskId1 = json["_id"]
        json = commandeAPI.createTaskMoveProductXFromStockAToStockB(factoryId, "Move Task secod", productId2, stockAId, stockBId)
        taskId2 = json["_id"]

        json = commandeAPI.createOperationMoveRobotTo(factoryId, mir100Id, (3.1, 2.5, 35/180*3.1415927))
        ope1 = json["_id"]
        testoperation = commandeAPI.testoperation(factoryId,ope1)
        json = commandeAPI.createOperationHuman(factoryId, Michel, [3.1, 2.5, 35/180*3.1415927], texte="Deplacer les objets", previous=ope1)
        ope2 = json["_id"]
        json = commandeAPI.createOperationHuman(factoryId, Mhammed, [3.1, 2.5, 35/180*3.1415927], ["Regarder Michel travailler","Analyser le temps qui passe","rediger le rapport d'activité"], previous=ope1)
        ope3 = json["_id"]
        json = commandeAPI.createOperationMoveRobotTo(factoryId, mir100Id, (8.1, 9.5, 35/180*3.1415927),previous=ope2)
        ope4 = json["_id"]
        commandeAPI.updatestatus(factoryId,"operation",ope3,"toDoAcknowledge")
        commandeAPI.updatestatus(factoryId,"operation",ope1,"doing")
        commandeAPI.updatestatus(factoryId,"operation",ope1,"done")
        commandeAPI.updatestatus(factoryId,"operation",ope2,"toDoAcknowledge")
        commandeAPI.updatestatus(factoryId,"operation",ope3,"doing")
        commandeAPI.updatestatus(factoryId,"operation",ope2,"doing")
        commandeAPI.updatestatus(factoryId,"operation",ope2,"done")
        commandeAPI.updatestatus(factoryId,"operation",ope4,"doing")
        commandeAPI.updatestatus(factoryId,"operation",ope4,"done")
        commandeAPI.updatestatus(factoryId,"operation",ope3,"done")

        json = commandeAPI.createProduct(factoryId, "iPhone 10 RAWPART", "iPhone 10 ABCDEF TOP")
        produit1 = json["_id"]
        json = commandeAPI.updateobject(factoryId, "product", produit1, {"reference":"iPhone 10 ABCDEFG TOP"})

        json = commandeAPI.createProduct(factoryId, "iPhone 10 RAWPART", "iPhone 10 ABCDEF Bottom")
        produit2 = json["_id"]
        json = commandeAPI.createTaskMoveProductXFromStockAToStockB(factoryId, "Move Task 1", produit1, stockAId, stockBId)
        taskId = json["_id"]

        Angle=Quaternion(axis=[0.0, 1.0, 0.0], degrees=90) #de l'axe Z à l'axe X
        json = commandeAPI.createStock(factoryId, "Machine A Stock in 1", "out", position={
            "position":{"x": 0.0 , "y": 0.1, "z": 0.8},"rotation":{"qx": Angle.x, "qy": Angle.y, "qz": Angle.z, "qw":  Angle.w}}) # stockin machine est un stock in robot
        stockMachineAin1 = json["_id"]
        json = commandeAPI.createStock(factoryId, "Machine A Stock in 2", "out", position={
            "position":{"x": 0.5 , "y": 0.1, "z": 0.8},"rotation":{"qx": Angle.x, "qy": Angle.y, "qz": Angle.z, "qw":  Angle.w}}) # stockin machine est un stock in robot
        stockMachineAin2 = json["_id"]
        Angle=Quaternion(axis=[1.0, 0.0, 0.0], degrees=-90) #de l'axe Z à l'axe Y
        json = commandeAPI.createStock(factoryId, "Machine A Stock out", "in", position={
            "position":{"x": 1.9 , "y": 0.1, "z": 0.8},"rotation":{"qx": Angle.x, "qy": Angle.y, "qz": Angle.z, "qw":  Angle.w}}) # stockout machine est un stock in robot
        stockMachineAout = json["_id"]

        json = commandeAPI.createMachine(factoryId,"chaine de fabrication",[],[])
        machineId = json["_id"]
        # moveMachine(factoryId,machineId,{"position":{"x": 1.0 , "y": 5.1, "z": 0.0},"rotation":{"qx": 0.0, "qy": 0.0, "qz": 0.0, "qw":  1.0}})

        json = commandeAPI.createJob(factoryId, "test", "iPhone 10 super perso")

        json = commandeAPI.createProduct(factoryId, "iPhone 10 RAWPART", "iPhone 10 ABCDEF TOP")
        produit1 = json["_id"]
        json = commandeAPI.createProduct(factoryId, "iPhone 10 RAWPART", "iPhone 10 ABCDEF Bottom")
        produit2 = json["_id"]
        json = commandeAPI.createTaskMoveProductXFromStockAToStockB(factoryId, "Move Task 1", produit1, stockAId, stockMachineAin1)
        taskId1 = json["_id"]
        json = commandeAPI.createTaskMoveProductXFromStockAToStockB(factoryId, "Move Task 2", produit2, stockAId, stockMachineAin2)
        taskId2 = json["_id"]
        json = commandeAPI.createTaskMoveProductXFromStockAToStockB(factoryId, "Move Task 3", produit2, stockMachineAout, stockBId)
        taskId3 = json["_id"]

        json = commandeAPI.defineNewJob(factoryId,"iPhone 10",[taskId1,taskId2,taskId3])
        newjob = json["_id"]
        json = commandeAPI.duplicatetask(factoryId,taskId1,"Move Task 1 origine")
        newduplicatedtask = json["_id"]

        json = commandeAPI.createOrder(factoryId, "Commande Client 1", "iPhone 10", 5)
        orderiPhone10 = json["_id"]
        FindedUnseenOrder = commandeAPI.findINfactory(factoryId,"order",orderStatus="toDo")
        json = commandeAPI.duplicatetask(factoryId,commandeAPI.findINfactory(factoryId,"task",name="Move Task 1")[0],"essai",named = True)
        newduplicatedtask = json["_id"]
        json = commandeAPI.createMetaResource(factoryId, "UR5+MIR100", "pickandmove", [mir100Id, ur5Id])
        metaR = json["_id"]
    else:
        factoryId = commandeAPI.findfactory(name="Factory LINEACT Test Fabrice")[0]
        # mir100Id = findINfactory(factoryId, "robot", name="mir100_Arm")[0]
        # ur5Id = findINfactory(factoryId, "robot", name="ur5_1")[0]
    

    # Machine1 = createMachine(factoryId, "Machine de Production", [stockMachineAin,stockMachineAout], [])
    # updateobject(factoryId,"machine",Machine1,{"transform2D":{"x":1,"y":1,"theta":90}})
    # createOperationMoveRobotTo(factoryId, mir100ArmId, 6, 1, 0
    print("done")
    testmove()
    # lock = thread.allocate_lock()
    # thread.start_new_thread(myfunction, ("Thread #: 1", 2, lock))
    # thread.start_new_thread(myfunction, ("Thread #: 2", 2, lock))