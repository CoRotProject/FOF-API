# coding: utf8
# Copyright 2021 Fabrice DUVAL
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

machinecapabilities = {}
# global positions :
positions = {
    "M1":{"x":36.25, "y":2.09, "theta":138.4, },
    "M2":{"x":33.00, "y":-2.40, "theta":135.1, },
    "M3":{"x":16.44, "y":-5.0, "theta":180.0, },
    "M4":{"x":15.00, "y":3.50, "theta":6.29, },
    "LU":{"x":3.31, "y":-3.43, "theta":0.11, },
    "output":{"x":43.19, "y":23.15, "theta":-91.35, },
    # "output":{"x":40.66, "y":5.90, "theta":30.44, },
}

machines = {"M1":[{'category':'production', 'capability':'01-cut',          'duration':8.0},
                {'category':'production', 'capability':'02-forming',        'duration':13.0},
                {'category':'production', 'capability':'03-shearing',       'duration':18.0},
                {'category':'production', 'capability':'04-bending',        'duration':20.0},
                {'category':'production', 'capability':'05-casting',        'duration':12.0},
                {'category':'production', 'capability':'06-die_casting',    'duration':14.0},
                {'category':'production', 'capability':'07-joining',        'duration':17.0},
                {'category':'production', 'capability':'08-press_fit',      'duration':18.0},
                {'category':'production', 'capability':'09-painting',       'duration':15.0},
                {'category':'production', 'capability':'10-labeling',       'duration':12.0},
                {'category':'production', 'capability':'11-clean',          'duration':15.0},],
            "M2":[{'category':'production', 'capability':'01-cut',          'duration':16.0},
                {'category':'production', 'capability':'02-forming',        'duration':16.0},
                {'category':'production', 'capability':'03-shearing',       'duration':11.0},
                {'category':'production', 'capability':'04-bending',        'duration':17.0},
                {'category':'production', 'capability':'05-casting',        'duration':999.0},
                {'category':'production', 'capability':'06-die_casting',    'duration':18.0},
                {'category':'production', 'capability':'07-joining',        'duration':15.0},
                {'category':'production', 'capability':'08-press_fit',      'duration':17.0},
                {'category':'production', 'capability':'09-painting',       'duration':17.0},
                {'category':'production', 'capability':'10-labeling',       'duration':18.0},
                {'category':'production', 'capability':'11-clean',          'duration':19.0},],
            "M3":[{'category':'production', 'capability':'01-cut',          'duration':16.0},
                {'category':'production', 'capability':'02-forming',        'duration':19.0},
                {'category':'production', 'capability':'03-shearing',       'duration':15.0},
                {'category':'production', 'capability':'04-bending',        'duration':11.0},
                {'category':'production', 'capability':'05-casting',        'duration':10.0},
                {'category':'production', 'capability':'06-die_casting',    'duration':12.0},
                {'category':'production', 'capability':'07-joining',        'duration':16.0},
                {'category':'production', 'capability':'08-press_fit',      'duration':19.0},
                {'category':'production', 'capability':'09-painting',       'duration':11.0},
                {'category':'production', 'capability':'10-labeling',       'duration':15.0},
                {'category':'production', 'capability':'11-clean',          'duration':9.0},],
            "M4":[{'category':'production', 'capability':'01-cut',          'duration':9.0},
                {'category':'production', 'capability':'02-forming',        'duration':14.0},
                {'category':'production', 'capability':'03-shearing',       'duration':12.0},
                {'category':'production', 'capability':'04-bending',        'duration':15.0},
                {'category':'production', 'capability':'05-casting',        'duration':17.0},
                {'category':'production', 'capability':'06-die_casting',    'duration':13.0},
                {'category':'production', 'capability':'07-joining',        'duration':14.0},
                {'category':'production', 'capability':'08-press_fit',      'duration':8.0},
                {'category':'production', 'capability':'09-painting',       'duration':11.0},
                {'category':'production', 'capability':'10-labeling',       'duration':13.0},
                {'category':'production', 'capability':'11-clean',          'duration':17.0},],
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

def createfullmachine(factoryid,name):
        returnvalue = {}
        stockinput = commandeAPI.createStock(factoryid, name + " in", "in")
        returnvalue["in"] = stockinput["_id"]
        stockoutput = commandeAPI.createStock(factoryid, name + " out", "out")
        returnvalue["out"] = stockoutput["_id"]
        returnvalue["machine"] = commandeAPI.createMachine(factoryid, name, [returnvalue["in"], returnvalue["out"]], machines[name], position=positions[name],)["_id"]
        commandeAPI.updateobject(factoryid, "stock", returnvalue["in"], {"link":returnvalue["machine"]})
        commandeAPI.updateobject(factoryid, "stock", returnvalue["out"], {"link":returnvalue["machine"]})
        return returnvalue

if __name__ == "__main__":
    Regeneration = True
    Newfactoryid = False
    renewmap = True
    nommap = "..\\Visualisation\\Madrillet.png"
    scalemap = [(-20.5, -34.2, 0.0), 0.05]
    print(commandeAPI.urlTemplate)
    print(commandeAPI.urlTemplateFactory)
    nomfact = "Factory LINEACT Mario"
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

        #Create Robots
        mirArm = createRobot(factoryid, "mir100_Arm", "mir100", [{"category": "transport"},{"category": "wait"}])
        mirCapitaine = createRobot(factoryid, "mir100_Capitaine", "mir100", [{"category": "transport"},{"category": "wait"}])
        ur10 = createRobot(factoryid, "ur10_1", "ur10", [{"category": "grab"},{"category": "wait"}])
        ur5 = createRobot(factoryid, "ur5_1", "ur5", [{"category": "grab"},{"category": "wait"}])
        commandeAPI.updateRobotPoseRandom(factoryid, mirArm["robot"])
        commandeAPI.updateRobotPoseRandom(factoryid, mirCapitaine["robot"])
        commandeAPI.updateRobotPoseRandom(factoryid, ur10["robot"])
        commandeAPI.updateRobotPoseRandom(factoryid, ur5["robot"])

        # Create Machines
        m1 = createfullmachine(factoryid, "M1")
        m2 = createfullmachine(factoryid, "M2")
        m3 = createfullmachine(factoryid, "M3")
        m4 = createfullmachine(factoryid, "M4")

        # Create Stock
        stockinput = commandeAPI.createStock(factoryid, "LU", "out",position2d=positions["LU"])

        # Create False Rawpart for tasks prototype
        # raw4job1 = commandeAPI.createProduct(factoryid, "rawpartgeneric", "Raw Part Job 1")["_id"]
        # raw4job2 = commandeAPI.createProduct(factoryid, "rawpartgeneric", "Raw Part Job 2")["_id"]
        # raw4job3 = commandeAPI.createProduct(factoryid, "rawpartgeneric", "Raw Part Job 3")["_id"]
        # raw4job4 = commandeAPI.createProduct(factoryid, "rawpartgeneric", "Raw Part Job 4")["_id"]
        # raw4job5 = commandeAPI.createProduct(factoryid, "rawpartgeneric", "Raw Part Job 5")["_id"]
        #Creates Tasks of Jobs 
        J1_T1 = commandeAPI.createTaskProduce(factoryid, "J1_T1_gen", "01-cut", "Job1_T1_end", ["Raw Part Job 1"], [])["_id"]
        J1_T2 = commandeAPI.createTaskProduce(factoryid, "J1_T2_gen", "02-forming", "Job1_T2_end", ["Job1_T1_end"], [])["_id"]
        J1_T3 = commandeAPI.createTaskProduce(factoryid, "J1_T3_gen", "03-shearing", "Job1_T3_end", ["Job1_T2_end"], [])["_id"]

        J2_T1 = commandeAPI.createTaskProduce(factoryid, "J2_T1_gen", "04-bending", "Job2_T1_end", ["Raw Part Job 2"], [])["_id"]
        J2_T2 = commandeAPI.createTaskProduce(factoryid, "J2_T2_gen", "05-casting", "Job2_T2_end", ["Job1_T1_end"], [])["_id"]
        J2_T3 = commandeAPI.createTaskProduce(factoryid, "J2_T3_gen", "06-die_casting", "Job2_T3_end", ["Job1_T2_end"], [])["_id"]

        J3_T1 = commandeAPI.createTaskProduce(factoryid, "J3_T1_gen", "07-joining", "Job3_T1_end", ["Raw Part Job 3"], [])["_id"]
        J3_T2 = commandeAPI.createTaskProduce(factoryid, "J3_T2_gen", "08-press_fit", "Job3_T2_end", ["Job2_T1_end"], [])["_id"]
        J3_T3 = commandeAPI.createTaskProduce(factoryid, "J3_T3_gen", "04-bending", "Job3_T3_end", ["Job3_T2_end"], [])["_id"]

        J4_T1 = commandeAPI.createTaskProduce(factoryid, "J4_T1_gen", "09-painting", "Job4_T1_end", ["Raw Part Job 4"], [])["_id"]
        J4_T2 = commandeAPI.createTaskProduce(factoryid, "J4_T2_gen", "10-labeling", "Job4_T2_end", ["Job4_T1_end"], [])["_id"]

        J5_T1 = commandeAPI.createTaskProduce(factoryid, "J5_T1_gen", "01-cut", "Job5_T1_end", ["Raw Part Job 5"], [])["_id"]
        J5_T2 = commandeAPI.createTaskProduce(factoryid, "J5_T2_gen", "11-clean", "Job5_T2_end", ["Job5_T1_end"], [])["_id"]

        # Create Job prototypes from previous tasks
        job1 = commandeAPI.defineNewJob(factoryid, "job 1", [J1_T1, J1_T2, J1_T3,])
        job2 = commandeAPI.defineNewJob(factoryid, "job 2", [J2_T1, J2_T2, J2_T3,])
        job3 = commandeAPI.defineNewJob(factoryid, "job 3", [J3_T1, J3_T2, J3_T3,])
        job4 = commandeAPI.defineNewJob(factoryid, "job 4", [J4_T1, J4_T2,])
        job5 = commandeAPI.defineNewJob(factoryid, "job 5", [J5_T1, J5_T2,])

    else:
        factoryid = commandeAPI.findfactory(name=nomfact)[0]
        if renewmap:
            commandeAPI.mapinfactory(factoryid, nommap, scalemap[0], scalemap[1])

    print("done")
