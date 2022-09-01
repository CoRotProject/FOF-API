# coding: utf8
# Copyright 2020 Fabrice DUVAL
# import requests
import os
import sys
# import random
import time
import base64
from pyquaternion import Quaternion
import Simulateurs.SimuMachineThreaded as simuMachine
import Simulateurs.SimuRobotThreaded as simuRobot
import commandeAPI
#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

print(os.getcwd())
print(base64.b64decode(base64.b64encode(b"Base 64 Valide")))

position = {
    "poste1":{"x":36.25, "y":2.09, "theta":138.4, },
    "poste2":{"x":33.00, "y":-2.40, "theta":135.1, },
    "poste3":{"x":16.44, "y":-5.0, "theta":180.0, },
    "poste4":{"x":15.00, "y":3.50, "theta":6.29, },
    "input":{"x":3.31, "y":-3.43, "theta":0.11, },
    "output":{"x":43.19, "y":23.15, "theta":-91.35, },
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

def getobjetstocks(factoryid, nomposte, typeobjet):
    retour = {}
    retour["main"] = commandeAPI.findINfactory(factoryid, typeobjet, name=nomposte)[0]
    retour["in"] = commandeAPI.findINfactory(factoryid, "stock", name=nomposte+" in")[0]
    retour["out"] = commandeAPI.findINfactory(factoryid, "stock", name=nomposte+" out")[0]
    return retour

if __name__ == "__main__":
    Regeneration = True
    Newfactoryid = False
    renewmap = False
    ResetMachineVirtuelle = False
    simulationMachine = False
    nommap = "..\\Visualisation\\Madrillet.png"
    scalemap = [(-20.5, -34.2, 0.0), 0.05]
    print(commandeAPI.urlTemplate)
    print(commandeAPI.urlTemplateFactory)
    nomfact = "Factory LINEACT Virtual"
    if Regeneration:
        # etape affacement de l'ancienne base
        listeinbase = commandeAPI.findfactory(name=nomfact)
        # listeinbase = findfactory(name="Factory LINEACT Test")
        effaceFactory = (len(listeinbase) != 1)  or Newfactoryid
        for usine in listeinbase:
            commandeAPI.deletepart(usine,typedata="product")                            # database product
            commandeAPI.deletepart(usine,typedata="taskMoveProductXFromStockAToStockB") # database task 1/1
            commandeAPI.deletepart(usine,typedata="operation")                          # database operation
            commandeAPI.deletepart(usine,typedata="job")                                # database job
            commandeAPI.deletepart(usine,typedata="jobdescription")                     # database jobdescription
            commandeAPI.deletepart(usine,typedata="order")                              # database order
            if effaceFactory:
                commandeAPI.deletepart(usine)
        if effaceFactory:
            json = commandeAPI.createFactory(nomfact)
            factoryid = json["_id"]
        else:
            factoryid = usine
        if listeinbase and ResetMachineVirtuelle:
            commandeAPI.deletepart(usine,typedata="resource")                           # database resource
            commandeAPI.deletepart(factoryid,typedata="machine")                        # database machine
            commandeAPI.deletepart(factoryid,typedata="stock")                          # database stock

        if ResetMachineVirtuelle:
            mirArm = createRobot(factoryid, "mir100_Arm", "mir100", [{"category": "transport"},{"category": "wait"}])
            mirCapitaine = createRobot(factoryid, "mir100_Capitaine", "mir100", [{"category": "transport"},{"category": "wait"}])
            ur10 = createRobot(factoryid, "ur10_1", "ur10", [{"category": "grab"},{"category": "wait"}])
            ur5 = createRobot(factoryid, "ur5_1", "ur5", [{"category": "grab"},{"category": "wait"}])
            commandeAPI.updateRobotPoseRandom(factoryid, mirArm["robot"])
            commandeAPI.updateRobotPoseRandom(factoryid, mirCapitaine["robot"])
            commandeAPI.updateRobotPoseRandom(factoryid, ur10["robot"])
            commandeAPI.updateRobotPoseRandom(factoryid, ur5["robot"])
            stockappro = commandeAPI.createStock(factoryid, "Stock Approvisionnement", "out", position2d=position["input"])["_id"]
            stockappro = json["_id"]
            stockout = commandeAPI.createStock(factoryid, "Stock sortie", "in", position2d=position["output"])["_id"]
            stockout = json["_id"]
            poste1 = commandeAPI.createPoste(factoryid, "Poste 1", position["poste1"])
            poste2 = commandeAPI.createPoste(factoryid, "Poste 2", position["poste2"])
            poste3 = commandeAPI.createPoste(factoryid, "Poste 3", position["poste3"])
            poste4 = commandeAPI.createPoste(factoryid, "Poste 4", position["poste4"])
            raw1 = commandeAPI.createProduct(factoryid, "cesi-corot RAWPART 1", "fourniture poste 1")["_id"]
            raw2 = commandeAPI.createProduct(factoryid, "cesi-corot RAWPART 2", "fourniture poste 2")["_id"]
            raw3 = commandeAPI.createProduct(factoryid, "cesi-corot RAWPART 3", "fourniture poste 3")["_id"]
            raw4 = commandeAPI.createProduct(factoryid, "cesi-corot RAWPART 4", "fourniture poste 4")["_id"]
            raw12 = commandeAPI.createProduct(factoryid, "cesi-corot inter1-2", "fourniture poste 2 depuis 1")["_id"]
            raw24 = commandeAPI.createProduct(factoryid, "cesi-corot inter2-4", "fourniture poste 4 depuis 2")["_id"]
            raw34 = commandeAPI.createProduct(factoryid, "cesi-corot inter3-4", "fourniture poste 4 depuis 3")["_id"]
            produitout = commandeAPI.createProduct(factoryid, "cesi-corot Final", "produit final")["_id"]
            commandeAPI.updateobject(factoryid, "product", raw1, {"link":stockappro})
            commandeAPI.updateobject(factoryid, "product", raw2, {"link":stockappro})
            commandeAPI.updateobject(factoryid, "product", raw3, {"link":stockappro})
            commandeAPI.updateobject(factoryid, "product", raw4, {"link":stockappro})

            Fabrice = commandeAPI.createHumanResource(factoryid, "Fabrice", "operator" , [{"category": "transport"},{"category": "wait"},{"category": "grab"}])["_id"]
            Mhammed = commandeAPI.createHumanResource(factoryid, "M'hammed", "operator", [{"category": "transport"},{"category": "wait"},{"category": "grab"}])["_id"]
            
    else:
        factoryid = commandeAPI.findfactory(name=nomfact)[0]

    stockappro = commandeAPI.findINfactory(factoryid, "stock", name="Stock Approvisionnement")[0]
    stockout = commandeAPI.findINfactory(factoryid, "stock", name="Stock sortie")[0]
    poste1 = getobjetstocks(factoryid, "Poste 1","machine")
    poste2 = getobjetstocks(factoryid, "Poste 2","machine")
    poste3 = getobjetstocks(factoryid, "Poste 3","machine")
    poste4 = getobjetstocks(factoryid, "Poste 4","machine")
    mirArm = getobjetstocks(factoryid, "mir100_Arm","robot")
    mirCapitaine = getobjetstocks(factoryid, "mir100_Capitaine","robot")


    if renewmap:
        commandeAPI.mapinfactory(factoryid, nommap, scalemap[0], scalemap[1])

        # On simule les machines ?
    if simulationMachine:
        machine1 = simuMachine.Machine(1, factoryid, poste1["main"], vitesse=1, temps=10)
        machine2 = simuMachine.Machine(2, factoryid, poste2["main"], vitesse=1, temps=10)
        machine3 = simuMachine.Machine(3, factoryid, poste3["main"], vitesse=1, temps=10)
        machine4 = simuMachine.Machine(4, factoryid, poste4["main"], vitesse=1, temps=10)
        machine1.start()
        machine2.start()
        machine3.start()
        machine4.start()
        
        mirArmSim = simuRobot.RobotMir(1,factoryid, mirArm["main"], vitesse=5, temps=0.25)
        mirCapitaineSim = simuRobot.RobotMir(1,factoryid, mirCapitaine["main"], vitesse=5, temps=0.25)
        mirArmSim.start()
        mirCapitaineSim.start()
        
        print("done")
        try:
            while(True):
                time.sleep(10)
        except KeyboardInterrupt:
            machine1.terminate()
            machine2.terminate()
            machine3.terminate()
            machine4.terminate()
            mirArmSim.terminate()
            mirCapitaineSim.terminate()
        print("killed")
    print("done")
