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
import imp
import queue
import sys
from math import sqrt
import UR as robot_arm
import Commandes.commandeAPI as commandeAPI
import json
#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

try:
    nomfactory = sys.argv[2]
except IndexError:
    nomfactory = "Factory LINEACT Real"

try:
    nomrobot = sys.argv[3]
    Robot = robot_arm.arm(host=sys.argv[4])
except IndexError:
    nomrobot = "ur10_t"
    Robot = robot_arm.arm(hote="10.191.76.119")

# nomfactory = "Factory LINEACT Test Fabrice"
# nomfactory = "Factory LINEACT Real"
Robot_mode_list = {-1:"ROBOT_MODE_NO_CONTROLLER",
                    0:"ROBOT_MODE_DISCONNECTED",
                    1:"ROBOT_MODE_CONFIRM_SAFETY",
                    2:"ROBOT_MODE_BOOTING",
                    3:"ROBOT_MODE_POWER_OFF",
                    4:"ROBOT_MODE_POWER_ON",
                    5:"ROBOT_MODE_IDLE",
                    6:"ROBOT_MODE_BACKDRIVE",
                    7:"ROBOT_MODE_RUNNING",
                    8:"ROBOT_MODE_UPDATING_FIRMWARE",}
Safety_mode_list ={ 1:"SAFETY_MODE_NORMAL",
                    2:"SAFETY_MODE_REDUCED",
                    3:"SAFETY_MODE_PROTECTIVE_STOP",
                    4:"SAFETY_MODE_RECOVERY",
                    5:"SAFETY_MODE_SAFEGUARD_STOP",
                    6:"SAFETY_MODE_SYSTEM_EMERGENCY_STOP",
                    7:"SAFETY_MODE_ROBOT_EMERGENCY_STOP",
                    8:"SAFETY_MODE_VIOLATION",
                    9:"SAFETY_MODE_FAULT",
                    10:"SAFETY_MODE_VALIDATE_JOINT_ID",
                    11:"SAFETY_MODE_UNDEFINED_SAFETY_MODE",}
Program_state_list ={1:"STOPPED",
                    2:"PLAYING",
                    3:"PAUSED",}


class AgentGrab(threading.Thread):
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
        self.safetymode = None
        self.robotmode = None
        self.programstate = None
        self.currenttoolposition = None
        self.currenttoolspeed = None
        self.enmission = False
        self.missionid = -1
        self.infomission = []
        self.operationencours = []
        self.updateall()
        self.running = True

    def updateall(self):
        """update position ans status"""
        # self.connexion.wait_endmove()
        etat = self.connexion.lire_statut()
        self.programstate = Program_state_list[etat["Program_state"][0]]
        self.safetymode = Safety_mode_list[etat["Safety_Mode"][0]]
        self.robotmode = Robot_mode_list[etat["Robot_Mode"][0]]
        self.currenttoolposition = etat["Tool_vector_actual"]
        self.currenttoolspeed = etat["TCP_speed_actual"]

    def run(self):
        nbturn = 0
        while self.running:
            self.updateall()
            if self.programstate == "STOPPED":
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
                        # spécifique opération
                        scriptname = self.name[self.name.rfind(" ")+1:]+"/"+self.operationencours[1]["params"]["function"]+".ascript"
                        positiontogodb = self.operationencours[1]["params"]["position"]
                        positiontogo = [positiontogodb["position"][x] for x in ['x','y','z']] + [positiontogodb["rotation"][x] for x in ['qx','qy','qz','qw']]
                        print("play script " + scriptname + " at ", positiontogo)
                        if len(self.operationencours[1]["params"]["parameters"])>3:
                            parameters = json.loads(self.operationencours[1]["params"]["parameters"])
                        self.connexion.sendcommand("ur10_t/grab.ascript", position=[0.0, 0.9, 0.2, 0, 1, 0, 0], **parameters)
                        self.updateall()
                        waitloop = 0
                        while self.programstate == "STOPPED":
                            waitloop += 1
                            time.sleep(0.5)
                            self.updateall()
                            if waitloop > 10:
                                self.fifobase.put((self.operationencours[0], 'error'))
                                self.enmission = False
                                self.operationlist.task_done()
                                break

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

    opfifo = queue.Queue() # create FIFO of valide operation
    retfifo = queue.Queue() # create FIFO of return value for database

    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
    robotbase = commandeAPI.findINfactory(factoryid, "robot", name=nomrobot)[0]
    robot_agent = AgentGrab(nomfactory+" "+nomrobot, factoryid, Robot, opfifo, retfifo)
    fifo_agent = testoutput("fifo output", retfifo)

    # robot_agent = AgentOperationMir(1, nomfactory+" "+nom, factoryid, robotbase, nom, robotreel)
    # poste1 = createPoste(factoryid,"Poste test", {'x':12.40, 'y':-6.78, 'theta':90.49})

    # operation1 = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (11.0, -10.0, 70.0))["_id"] # vertical
    # operation2 = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (16.0, -4.0, -172.0), previous=operation1)["_id"] # vertical
    # operation3 = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0.0, 0.0, 90.0, poste1["in"]), previous=operation2)["_id"] # vertical
    # operation3 = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0.0, 0.0, 90.0, poste1["in"]))["_id"] # vertical
    # self.operations[valeur['operationType']].put([key, valeur])
    # opfifo.put(["1", {"transform2D":position["poste1"]}])
    # opfifo.put(["2", {"transform2D":position["poste2"]}])
    # opfifo.put(["3", {"transform2D":position["poste3"]}])
    # opfifo.put(["4", {"transform2D":position["poste4"]}])
    #commandeAPI.createOperationGrab(factoryidentity, ur5, [[0.383, -0.330, 0.066], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="grab")["_id"]
    operations = commandeAPI.findINfactory(factoryid, "operation", resourceInfo=robotbase)
    if len(operations)==0:
        operation1 = commandeAPI.createOperationGrab(factoryid, robotbase, [[0.0, 0.9, 0.2], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="grab", functionparameters=json.dumps({"delta_saisie":0.10}))["_id"] # vertical
    else:
        operation1 = operations[0]
    operationinfos = commandeAPI.getvalues(factoryid, "operation", operation1)

    opfifo.put(["1", operationinfos])





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
