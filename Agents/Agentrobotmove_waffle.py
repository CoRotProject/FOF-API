#!/usr/bin/env python2 
# coding: utf8
# Copyright 2020 Fabrice DUVAL

from __future__ import unicode_literals
from __future__ import print_function
import time
# import sys
# import os
# import glob
import threading
# import math
# import imp
import queue
import sys
from math import sqrt
import waffle
import Commandes.commandeAPI as commandeAPI
#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

# position = {"poste1":{"x":11.77, "y":-6.16, "theta": 4.0},
#              "poste2":{"x":16.53, "y":2.11, "theta": 90.88},
#              "poste3":{"x":35.02, "y":3.19, "theta": 7.01},
#              "poste4":{"x":30.60, "y":-4.59, "theta": -65.73},
#             }
position = {
    "poste1":{"x":36.25, "y":2.09, "theta":138.4, },
    "poste2":{"x":33.00, "y":-2.40, "theta":135.1, },
    "poste3":{"x":16.44, "y":-5.0, "theta":180.0, },
    "poste4":{"x":15.00, "y":3.50, "theta":6.29, },
    "input":{"x":3.31, "y":-3.43, "theta":0.11, },
    "output":{"x":43.19, "y":23.15, "theta":-91.35, },
    # "output":{"x":40.66, "y":5.90, "theta":30.44, },
}



nomfactory = "Factory LINEACT Real"
nomrobot = "waffle_pi"
# robotId = "60c2255e40c1958bd5bfa6b5"

def dist(x1, y1, x2, y2):
    return sqrt((x1-x2)**2+(y1-y2)**2)

class AgentDeplacement(threading.Thread):
    """status possible : offline, free, busy, error
    """
    def __init__(self, nom, lienbdd, lienrobot, opvalidfifo, retbasefifo):
        """lienbdd : id of factory, lienrobot : link to robot class, opvalidfifo : Queue of valid moveto, retbasefifo : link to update op status"""
        threading.Thread.__init__(self)
        self.name = nom
        self.factoryid = lienbdd
        self.connexion = lienrobot
        self.operationlist = opvalidfifo
        # self.operationencours = []
        self.fifobase = retbasefifo

        self.status = 'offline'
        self.posx = 0.0
        self.posy = 0.0
        self.theta = 0.0
        self.battery = 0.0
        self.enmission = False
        self.missionid = -1
        self.infomission = []
        self.operationencours = []
        self.updateall()
        self.running = True

    def getposition(self):
        """return updated position"""
        self.updateposition()
        return self.posx, self.posy, self.theta

    def updateposition(self):
        """update position"""
        self.posx, self.posy, self.theta = self.connexion.getposition()
        commandeAPI.updateobject(self.factoryid, "robot", commandeAPI.findINfactory(self.factoryid, "robot", name=self.connexion.mynom)[0], {"transform2D":{"x":self.posx,"y":self.posy,"theta":self.theta}})
    def updateall(self):
        """update position ans status"""
        #on met tout dans etat, afin de reprendre la position, le status...
        etat = self.connexion.getstatus()
        self.status = etat["status"]
        self.updateposition()
        #if status == "Ready":
        #    self.status = "free"
        #elif status == "Error":
        #    self.status = "error"
        #else:
        #    self.status = "busy"

    #def testOP(self):
    #    robotbase = commandeAPI.findINfactory(self.factoryid, "robot", name=self.name)[0]
    #    operationTest = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (-0.5, 1, 0),name="test1")["_id"]


    def run(self):
        nbturn = 0
        while self.running:
            self.updateall()
            if self.status == "free":
                if self.enmission: # mission en cours et free => mission finie
                    self.fifobase.put((self.operationencours[0], 'done'))
                    self.enmission = False
                    self.operationlist.task_done()
                    nbturn = 0
                else: # no running mission
                    if self.operationlist.empty(): # no pending mission
                        if nbturn == 1: # limit "free" printing
                            print("free")
                        elif nbturn >= 20:
                            nbturn = 0
                        nbturn += 1
                    else: #there is a least 1 mission
                        self.status = 'busy'
                        self.enmission = True
                        self.operationencours = self.operationlist.get()
                        self.fifobase.put((self.operationencours[0], 'doing'))
                        # positiontogo = self.operationencours[1] # Need traduction from database
                        positiontogo = commandeAPI.findrealposition(self.factoryid, self.operationencours[1])
                        print("Real Go To = (", positiontogo['x'], positiontogo['y'], positiontogo['theta'], ")")
                        self.missionid = self.connexion.go((positiontogo['x'], positiontogo['y'], positiontogo['theta'])) # specific waffle missionid
                        time.sleep(0.5) # donner le temps à réagir
            else: # not free => robot move
                if self.missionid == -1: # no running mission specific waffle
                    if self.operationencours:
                        self.fifobase.put((self.operationencours[0], 'error'))
                        self.operationencours = []
            time.sleep(1)

    def terminate(self):
        """clean stop"""
        print("agent move killed")
        self.running = False

class testoutput(threading.Thread):
    """only to print output of fifo"""
    def __init__(self, nom, retbasefifo):
        threading.Thread.__init__(self)
        self.name = nom
        self.fifobase = retbasefifo
        self.running = True

    def run(self):
        """loop of fifo test"""
        nbturn = 0
        while self.running:
            if self.fifobase.empty(): # no pending mission
                if nbturn == 1: # limit "free" printing
                    print("noreturn")
                elif nbturn >= 20:
                    nbturn = 0
                nbturn += 1
            else:
                nbturn = 0
                print(self.fifobase.get())
            time.sleep(2)

    def terminate(self):
        """clean stop"""
        print("agent test killed")
        self.running = False

if __name__ == "__main__":
    Regenerationope = False
    print("Launch Robot move Agent " + nomrobot + " connected to database " + commandeAPI.urlTemplate)

    robotreel = waffle.Waffle(nom=nomrobot)

    opfifo = queue.Queue() # create FIFO of valide operation
    retfifo = queue.Queue() # create FIFO of return value for database

    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
    robotbase = commandeAPI.findINfactory(factoryid, "robot", name=nomrobot)[0]
    robot_agent = AgentDeplacement(nomfactory+" "+nomrobot, factoryid, robotreel, opfifo, retfifo)
    fifo_agent = testoutput("fifo output", retfifo)

    # robot_agent = AgentOperationWaffle(1, nomfactory+" "+nom, factoryid, robotbase, nom, robotreel)
    # poste1 = createPoste(factoryid,"Poste test", {'x':12.40, 'y':-6.78, 'theta':90.49})

    # operation1 = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (11.0, -10.0, 70.0))["_id"] # vertical
    # operation2 = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (16.0, -4.0, -172.0), previous=operation1)["_id"] # vertical
    # operation3 = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0.0, 0.0, 90.0, poste1["in"]), previous=operation2)["_id"] # vertical
    # operation3 = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0.0, 0.0, 90.0, poste1["in"]))["_id"] # vertical
    # self.operations[valeur['operationType']].put([key, valeur])
    opfifo.put(["1", {"transform2D":position["poste1"]}])
    # opfifo.put(["2", {"transform2D":position["poste2"]}])
    # opfifo.put(["3", {"transform2D":position["poste3"]}])
    # opfifo.put(["4", {"transform2D":position["poste4"]}])




    robot_agent.start()
    fifo_agent.start()
    print("done")
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        robot_agent.terminate()
        fifo_agent.terminate()
    print("killed")
