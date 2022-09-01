#!/usr/bin/env python2 
# coding: utf8
# Copyright 2020 Fabrice DUVAL

from __future__ import unicode_literals
from __future__ import print_function
import time
import sys
import socket
# import mir
import Commandes.commandeAPI as commandeAPI
try:
    import rospy
    ROSenable = True
except ImportError:
    ROSenable = False

#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

# from lxml import etree as ET
# updateobject(factoryid,"machine",Machine1,{"transform2D":{"x":1,"y":1,"theta":90}})

nomfactory = "Factory CERI"
nomrobot = "CERI_AGV"

try:
    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
except IndexError:
    print("Base inacessible. Pause puis quitte")
    time.sleep(10)
    exit("Base non valide")

try:
    ceri_agv = commandeAPI.findINfactory(factoryid,"robot", name=nomrobot)[0]
except IndexError:
    print("robot {} inacessible. Pause puis quitte".format(nomrobot))
    time.sleep(10)
    exit("Robot non valide")

# import os
# files = os.listdir('.')
# for name in files:
    # print(name)

robot = commandeAPI.getvalues(factoryid, "robot", ceri_agv)

Lastpos = [robot['transform2D']['x'], robot['transform2D']['y'], robot['transform2D']['theta'], ] # x, y, Theta

print("Position orgine BDD",Lastpos)


while True:
    status = mirrobot.getstatus()
    CurrentPos = [float(status['x']), float(status['y']), float(status['theta']),]
    deltapos = ((CurrentPos[0]-Lastpos[0])**2 + (CurrentPos[1]-Lastpos[1])**2)**0.5
    deltaangle = (CurrentPos[2]-Lastpos[2]) % 360
    if deltapos > 0.01 or deltaangle > 1: # on fait kke chose si déplacement > 1cm ou deltaangle > 1°
        print(Lastpos, end='')
        print(" ==> ", end='')
        print(CurrentPos)
        commandeAPI.updateobject(factoryid, "robot", ceri_agv, {"transform2D":{"x":CurrentPos[0],"y":CurrentPos[1],"theta":CurrentPos[2]}})
        Lastpos = CurrentPos
    time.sleep(0.5) #update toute les 500ms

