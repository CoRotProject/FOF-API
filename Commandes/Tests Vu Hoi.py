# coding: utf8
# Copyright 2020 Fabrice DUVAL
# import requests
# import random
import sys
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
    factoryId = commandeAPI.findfactory(name="Factory LINEACT Test Fabrice")[0]
    mir100Id1 = commandeAPI.findINfactory(factoryId, "robot", name="mir100_Arm")[0]
    mir100Id2 = commandeAPI.findINfactory(factoryId, "robot", name="mir100_Capitaine")[0]
    a1 = commandeAPI.createOperationMoveRobotTo(factoryId, mir100Id1, (0, 0, 0))["_id"]
    a1 = commandeAPI.createOperationMoveRobotTo(factoryId, mir100Id1, (12, 12, 45),previous=a1)["_id"]
    a1 = commandeAPI.createOperationMoveRobotTo(factoryId, mir100Id1, (12, 0, 78),previous=a1)["_id"]
    a1 = commandeAPI.createOperationMoveRobotTo(factoryId, mir100Id1, (0, 12, 156),previous=a1)["_id"]
    a2 = commandeAPI.createOperationMoveRobotTo(factoryId, mir100Id2, (6, 6, 90))["_id"]
    a2 = commandeAPI.createOperationMoveRobotTo(factoryId, mir100Id2, (-1, 6, 0),previous=a2)["_id"]
    a2 = commandeAPI.createOperationMoveRobotTo(factoryId, mir100Id2, (5, 8, 45),previous=a2)["_id"]
    a2 = commandeAPI.createOperationMoveRobotTo(factoryId, mir100Id2, (9, 4, 135),previous=a2)["_id"]
    a2 = commandeAPI.createOperationMoveRobotTo(factoryId, mir100Id2, (0, 0, 15),previous=a2)["_id"]


if __name__ == "__main__":
    Regeneration = True
    NewFactoryId = False
    print(commandeAPI.urlTemplate)
    print(commandeAPI.urlTemplateFactory)
    if Regeneration:
        # etape affacement de l'ancienne base
        listeinbase = commandeAPI.findfactory(name="Factory Vu Hoi")
        # listeinbase = findfactory(name="Factory LINEACT Test")
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
            json = commandeAPI.createFactory("Factory Vu Hoi")
            factoryId = json["_id"]
        else:
            factoryId = usine

        commandeAPI.mapinfactory(factoryId, "..\\Visualisation\\Vu_Hoi.png", (-21.0, -33.2, 0.0), 0.05)
        json = commandeAPI.createRobotResource(factoryId, "robot0", "mir100",[{"category": "transport"},{"category": "wait"}])
        robot0 = json["_id"]
        json = commandeAPI.createRobotResource(factoryId, "robot1", "mir100",[{"category": "transport"},{"category": "wait"}])
        robot1 = json["_id"]
        commandeAPI.updateRobotPoseRandom(factoryId, robot0)
        commandeAPI.updateRobotPoseRandom(factoryId, robot1)

        json = commandeAPI.createHumanResource(factoryId, "Michel", "operator", [{"category": "transport"},{"category": "wait"},{"category": "grab"}])
        Michel = json["_id"]

        json = commandeAPI.createOperationMoveRobotTo(factoryId, robot0, (3.1, 2.5, 35/180*3.1415927))
        ope1 = json["_id"]
        testoperation = commandeAPI.testoperation(factoryId,ope1)
        json = commandeAPI.createOperationHuman(factoryId, Michel, "Deplacer les objets", (3.1, 2.5, 35/180*3.1415927),previous=ope1)
        ope2 = json["_id"]
        json = commandeAPI.createOperationMoveRobotTo(factoryId, robot0, (8.1, 9.5, 35/180*3.1415927),previous=ope2)
        ope3 = json["_id"]
        commandeAPI.updatestatus(factoryId,"operation",ope1,"doing")
        commandeAPI.updatestatus(factoryId,"operation",ope1,"done")
        commandeAPI.updatestatus(factoryId,"operation",ope2,"toDoAcknowledge")
        commandeAPI.updatestatus(factoryId,"operation",ope2,"doing")
        commandeAPI.updatestatus(factoryId,"operation",ope2,"done")
        commandeAPI.updatestatus(factoryId,"operation",ope3,"doing")
        commandeAPI.updatestatus(factoryId,"operation",ope3,"done")


    else:
        factoryId = commandeAPI.findfactory(name="Factory Vu Hoi")[0]
        # mir100Id = findINfactory(factoryId, "robot", name="mir100_Arm")[0]
        # ur5Id = findINfactory(factoryId, "robot", name="ur5_1")[0]
    

    # Machine1 = createMachine(factoryId, "Machine de Production", [stockMachineAin,stockMachineAout], [])
    # updateobject(factoryId,"machine",Machine1,{"transform2D":{"x":1,"y":1,"theta":90}})
    # createOperationMoveRobotTo(factoryId, mir100ArmId, 6, 1, 0
    print("done")
    # testmove()
    # lock = thread.allocate_lock()
    # thread.start_new_thread(myfunction, ("Thread #: 1", 2, lock))
    # thread.start_new_thread(myfunction, ("Thread #: 2", 2, lock))