# coding: utf8
# Copyright 2020 Fabrice DUVAL
from __future__ import print_function
import time
import threading
import math
import sys
# import requests
# import pymongo
# sys.path.append("..\\Commandes")
import Commandes.commandeAPI as commandeAPI
#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

class RobotMir(threading.Thread):
    def __init__(self, threadID, factoryid, robotid, vitesse=1, temps=0.1):
        # vitesse est un facteur multiplicatif de la vitesse
        # temps est le temps entre deux rafraichissements
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.robotid = robotid
        self.factoryid = factoryid
        whoiam = commandeAPI.getvalues(self.factoryid, "resource", self.robotid)
        self.x = whoiam["transform2D"]["x"]
        self.y = whoiam["transform2D"]["y"]
        self.theta = whoiam["transform2D"]["theta"]
        self.vitesse = vitesse
        self.temps = temps
        commandeAPI.updatestatus(self.factoryid, "robot", self.robotid, "free")
        self.running = True
        try:
            self.speed = whoiam["internalParams"]["speed"]
        except:
            self.speed = 10
        try:
            self.thetaspeed = whoiam["internalParams"]["thetaspeed"]
        except:
            self.thetaspeed = 100
        try:
            self.timegrab = whoiam["internalParams"]["grab"]
        except:
            self.timegrab = 5
        try:
            self.timerelease = whoiam["internalParams"]["release"]
        except:
            self.timerelease = self.timegrab
        
    def run(self): # Première version : consomme beaucoup de bande passante, intérogation de chaque opération précédante
        while self.running:
            findOperation = commandeAPI.findINfactory(self.factoryid, "operation",status="toDo", resourceInfo=self.robotid)
            # if len(FindedUnseenOrder)>0:
            for operationtodo in findOperation:
                allInfo = commandeAPI.getvalues(self.factoryid, "operation", operationtodo)
                runIt = True
                for operation in allInfo['precedenceOperationInfo']:
                    try:
                        if commandeAPI.getvalues(self.factoryid, "operation", operation)['status'] == 'done':
                            continue
                        else:
                            runIt = False
                            break
                    except:
                        runIt = False
                        break
                if runIt:
                    commandeAPI.updatestatus(self.factoryid, "robot", self.robotid, "busy")
                    commandeAPI.updatestatus(self.factoryid, "operation", operationtodo, "doing")
                    print("execution de {}".format(allInfo["_id"]))
                    positiontogo = self.findrealposition(allInfo["params"])
                    self.moveTo(positiontogo)
                    commandeAPI.updatestatus(self.factoryid, "operation", operationtodo, "done")
                    commandeAPI.updatestatus(self.factoryid, "robot", self.robotid, "free")
                    break
                else:
                    print("execution de {} impossible".format(allInfo["_id"]))
            print(".", end='', flush=True)  
            time.sleep(1)
    
    def findrealposition(self, parametres):
        posx = parametres["transform2D"]['x']
        posy = parametres["transform2D"]['y']
        theta = parametres["transform2D"]['theta']
        if "stockInfo" in parametres:
            stock = commandeAPI.getvalues(self.factoryid, "stock", parametres['stockInfo'])
            stockpos = stock["transform2D"]
            stox, stoy, stothetadeg, stothetarad = stockpos['x'], stockpos['y'], stockpos['theta'], stockpos['theta']/180*math.pi
            xavant = stox + posx * math.cos(stothetarad) - posy * math.sin(stothetarad)
            yavant = stoy + posy * math.cos(stothetarad) + posx * math.sin(stothetarad)
            tavant = (stothetadeg + theta) % 360
            tavant = tavant if tavant <= 180 else tavant - 360
            if 'link' in stock:
                lien = stock["link"]
                while lien:
                    machine = commandeAPI.getvalues(self.factoryid, "machine", lien)
                    machinepos = machine["transform2D"]
                    machx, machy, macht, machtrad = machinepos['x'], machinepos['y'], machinepos['theta'], machinepos['theta']/180*math.pi
                    xapres = machx + xavant * math.cos(machtrad) - yavant * math.sin(machtrad)
                    yapres = machy + yavant * math.cos(machtrad) + xavant * math.sin(machtrad)
                    tapres = (macht + tavant) % 360
                    tapres = tapres if tapres <= 180 else tapres - 360
                    xavant, yavant, tavant = xapres, yapres, tapres
                    if 'link' in machine:
                        lien = machine['link']
                    else:
                        lien = None
            return {'x':xavant,'y':yavant, 'theta':tavant}
        else:
            return {'x':posx,'y':posy, 'theta':theta}

    def updatepos(self):
        print("({},{},{})".format(self.x, self.y, self.theta))
        commandeAPI.updateobject(self.factoryid, "resource", self.robotid, {"transform2D":{"x":self.x, "y":self.y, "theta":self.theta}})

    def deltaangle(self, before, after):
        ecart = after - before
        ecart += -360 if (ecart > 180) else 360 if (ecart <= -180) else 0
        thetaspeed = self.thetaspeed/10*self.vitesse
        if abs(ecart) < thetaspeed:
            return after
        temp = before + math.copysign(thetaspeed, ecart)
        temp += -360 if (temp > 180) else 360 if (temp < -180) else 0
        return temp

    def moveTo(self, position):
        print("go to (x,y,theta) = ({},{},{})".format(position["x"], position["y"], position["theta"]))
        dx = position["x"]-self.x
        dy = position["y"]-self.y
        newtheta = math.degrees(math.atan2(dy, dx))
        while abs(self.theta - newtheta) > 0.1:
            self.theta = self.deltaangle(self.theta, newtheta)
            self.updatepos()
            time.sleep(self.temps)
        self.theta = newtheta
        self.updatepos()
        while abs(self.x - position["x"]) +  abs(self.y - position["y"]) > 0.01:
            move = min(self.speed/10*self.vitesse, math.hypot(self.x - position["x"], self.y - position["y"]))
            self.x += round(move * math.cos(math.radians(newtheta)), 4)
            self.y += round(move * math.sin(math.radians(newtheta)), 4)
            time.sleep(self.temps)
            self.updatepos()
        self.x = position["x"]
        self.y = position["y"]
        self.updatepos()
        while abs(self.theta - position["theta"]) > 0.1:
            self.theta = self.deltaangle(self.theta, position["theta"])
            self.updatepos()
            time.sleep(self.temps)
        self.theta = position["theta"]
        self.updatepos()
    
    def terminate(self):
        commandeAPI.updatestatus(self.factoryid, "robot", self.robotid, "offline")
        self.running = False

  
if __name__ == "__main__":
    Regeneration = False
    # factoryid = commandeAPI.findfactory(name="Factory LINEACT simulated")[0]
    factoryid = commandeAPI.findfactory(name="Factory LINEACT Real")[0]
    #mir100_Arm mir100
    if Regeneration:
        commandeAPI.deletepart(factoryid, typedata="resource", robotType="Mir100") # on detruit tous les robots Mir100
        commandeAPI.deletepart(factoryid, typedata="operation", operationType="robotmove")
        mir100ArmId = commandeAPI.createRobotResource(factoryid, "mir100_Arm", "mir100", [{"category": "transport"}, {"category": "wait"}, {"category": "grab"}])["_id"]
        mir100CapitaineId = commandeAPI.createRobotResource(factoryid, "mir100_Capitaine", "mir100", [{"category": "transport"}, {"category": "wait"}])["_id"]
        commandeAPI.updateRobotPoseRandom(factoryid, mir100ArmId)
        jsonchgt1robot = commandeAPI.updateobject(factoryid, "resource", mir100ArmId, {"internalParams":{"speed":1.0, "thetaspeed":30, "grab":3.0, "release":1.0}})
        jsonchgt2robot = commandeAPI.updateobject(factoryid, "resource", mir100ArmId, {"transform2D":{"x":1, "y":1, "theta":90.0,}})

        ope1 = commandeAPI.createOperationMoveRobotTo(factoryid, mir100ArmId, (1, 6, 180))["_id"]
        ope2 = commandeAPI.createOperationMoveRobotTo(factoryid, mir100ArmId, (6, 6, 90), previous=ope1)["_id"]
        ope3 = commandeAPI.createOperationMoveRobotTo(factoryid, mir100ArmId, (6, 1, 0), previous=ope2)["_id"]
        ope4 = commandeAPI.createOperationMoveRobotTo(factoryid, mir100ArmId, (1, 1, -90), previous=ope3)["_id"]

    else:
        mir100ArmId = commandeAPI.findINfactory(factoryid, "resource", name="mir100_Arm")[0]
        mir100CapitaineId = commandeAPI.findINfactory(factoryid, "resource", name="mir100_Capitaine")[0]

    Mir_Arm = RobotMir(1,factoryid, mir100ArmId, vitesse=1, temps=1)
    Mir_Capitaine = RobotMir(1,factoryid, mir100CapitaineId, vitesse=10, temps=1)
    Mir_Arm.start()
    Mir_Capitaine.start()

    print("done")
    try:
        while(True):
            time.sleep(10)
    except KeyboardInterrupt:
        Mir_Arm.terminate()
        Mir_Capitaine.terminate()
    print("killed")