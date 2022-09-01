#!/usr/bin/env python2 
# coding: utf8
# Copyright 2020 Fabrice DUVAL

from __future__ import unicode_literals
from __future__ import print_function
import time
import sys
# import socket
import mir
import threading
try:
    import rospy
    # from mirSupervisor.srv import *
    from mirMsgs.msg import *
    ROSenable = True
except ImportError:
    ROSenable = False
from FOF_API.Commandes import commandeAPI

#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

# Syntaxe
# UpdatePosMir url robotname
# url : full url of API (ex: http://robigdata.rorecherche:5000/)
# robotname name of the robot on the database

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

try:
    nom = sys.argv[2]
except IndexError:
    nom = "mir100_Arm"

try:
    nomfactory = sys.argv[3]
except IndexError:
    nomfactory = "Factory LINEACT Real"

# from lxml import etree as ET
# updateobject(factoryid,"machine",Machine1,{"transform2D":{"x":1,"y":1,"theta":90}})

debuglocal = False
# nomfactory = "Factory LINEACT Real"

try:
    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
except IndexError:
    print("Base inacessible. Pause puis quitte")
    time.sleep(10)
    exit("Base non valide")

try:
    Mir100 = commandeAPI.findINfactory(factoryid,"robot", name=nom)[0]
except IndexError:
    print("robot {} inacessible. Pause puis quitte".format(nom))
    time.sleep(10)
    exit("Robot non valide")

if debuglocal:
    mirrobot = mir.Mir(nom=nom, lienhttp='http://mir_arm.rorecherche/ajax/')
else:
    mirrobot = mir.Mir(nom=nom)

class RobotParamUpdater(threading.Thread):
    """définition de l'agent gerant les opérations des resources"""
    def __init__(self, robotlink, database, robotindb):
        threading.Thread.__init__(self)
        self.robotlink = robotlink
        self.factoryid = database
        self.robotid = robotindb
        self.MIR_Status = []
        self.mirstatusvalid = False
        self.robotstatus = {"state": -1, "mode": "", "msg": "", "uptime": 0.0, "moved": 0.0, "battery": 0.0, "battery_percentage": 0.0, "battery_time_left": 0, "eta":0.0}

        if ROSenable:
            rospy.init_node('db_updater')
            self.topicsub = rospy.Subscriber("/mir_status", MirStatus, self.rosmirstatuscallback)
            rospy.on_shutdown(self.terminate)

        robottemps = commandeAPI.getvalues(self.factoryid, "robot", self.robotid)
        self.lastpos = [robottemps['transform2D']['x'], robottemps['transform2D']['y'], robottemps['transform2D']['theta'], ] # x, y, Theta
        print("Position orgine BDD", self.lastpos)
        self.running = True
    
    def rosmirstatuscallback(self, data):
        if not rospy.is_shutdown():
            self.MIR_Status = data
            self.mirstatusvalid = True

    def run(self):
        while self.running:
            status = self.robotlink.getstatus()
            currentpos = [float(status['x']), float(status['y']), float(status['theta']),]
            deltapos = ((currentpos[0]-self.lastpos[0])**2 + (currentpos[1]-self.lastpos[1])**2)**0.5
            deltaangle = (currentpos[2]-self.lastpos[2]) % 360
            if deltapos > 0.01 or deltaangle > 1: # on fait kke chose si déplacement > 1cm ou deltaangle > 1°
                print(self.lastpos, end='')
                print(" ==> ", end='')
                print(currentpos)
                commandeAPI.updateobject(self.factoryid, "robot", self.robotid, {"transform2D":{"x":currentpos[0],"y":currentpos[1],"theta":currentpos[2]}})
                self.lastpos = currentpos
            if self.mirstatusvalid:
                self.robotstatus["state"] = self.MIR_Status.state
                self.robotstatus["mode"] = self.MIR_Status.mode
                self.robotstatus["msg"] = self.MIR_Status.msg
                self.robotstatus["uptime"] = self.MIR_Status.uptime
                self.robotstatus["moved"] = self.MIR_Status.moved
                self.robotstatus["battery"] = self.MIR_Status.battery
                self.robotstatus["battery_percentage"] = self.MIR_Status.battery_percentage
                self.robotstatus["battery_time_left"] = self.MIR_Status.battery_time_left
                self.robotstatus["eta"] = self.MIR_Status.eta
                commandeAPI.updateobject(self.factoryid, "robot", self.robotid, {"internalParams":self.robotstatus})

            time.sleep(1.0)

    def terminate(self):
        self.topicsub.unregister()
        self.running = False
        print("agent update param robot killed")

if __name__ == "__main__":
    robot = RobotParamUpdater(mirrobot, factoryid, Mir100)

    robot.start()
    print("done")
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        robot.terminate()

    print("killed 1")