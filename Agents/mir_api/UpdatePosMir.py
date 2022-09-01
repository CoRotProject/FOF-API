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
from FOF_API.Commandes import commandeAPI


# Syntaxe
# UpdatePosMir url robotname
# url : full url of API (ex: http://robigdata.rorecherche:5000/)
# robotname name of the robot on the database



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


        robottemps = commandeAPI.getvalues(self.factoryid, "robot", self.robotid)
        self.lastpos = [robottemps['transform2D']['x'], robottemps['transform2D']['y'], robottemps['transform2D']['theta'], ] # x, y, Theta
        print("Position orgine BDD", self.lastpos)
        self.running = True
        

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
        # self.topicsub.unregister()
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