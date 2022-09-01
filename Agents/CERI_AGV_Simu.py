#!/usr/bin/env python
from __future__ import unicode_literals
from __future__ import print_function
import json
import time
# import requests
import quaternionTransforms

WAFFLE_Status = ["offline", "free", "ShuttingDown", "internalprocess", "busy", "error"]

class CERI_AGV:
    def __init__(self, nom):
        self.mynom = nom
        self.x = 999.999
        self.y = 999.999
        self.theta = 0.0
        self.liststatus = []
        self.status = "internalProcess"
        self.battery = 100.0
        #self.jesuispret()
        self.status ="free"

    def initposition(self):
        print("try new position")


    def poseToMove(self, x, y, YawDegres):
        #transformation de l angle en yaw en quaternion
        quaternion = quaternionTransforms.euler_to_quaternion(quaternionTransforms.angleToRad(YawDegres),0,0)

        print("CERI_AGV_Déplacement_simulé")
        print("vers")
        print("x={}, y={}, wz={}({}°)".format(x, y, quaternion[2], YawDegres))
        time.sleep(3)
        print("3 secondes move !")
        self.x = x
        self.y = y
        self.theta = YawDegres
        return True

    def go(self, point):
        """move robot"""
        self.status = "busy"
        #query = self.serveur + "fabrice.php?action=go_to_position&x=" + str(point[0]) +"&y=" +  str(point[1]) + "&theta=" + str(point[2])
        result = self.poseToMove(point[0],point[1],point[2])
        print("Goal execution done!")
        self.status = "free"

    def pose_listener(self, msg):
        self.x = self.x + 0.1
        self.y = self.y + 0.1

    def getposition(self):
        return self.x, self.y, self.theta

    def getstatus(self):
        """get full sattus"""
        retour = {}
        retour['x'], retour['y'], retour['theta'] = self.getposition()
        retour['status'] = self.status
        retour['battery'] = self.battery

        return retour

if __name__ == '__main__':
    robot = CERI_AGV("CERI_AGV")
    print(robot.getstatus())
    while(True):
        position = [int(input("entrez la position en x : ")), int(input("entrez la position en y : ")), int(input("entrez la rotation : "))]
        print(robot.getstatus())
        if position[0] == 999:
            break
        if position[0] == -999:
            continue
        # rospy.init_node('movebase_client_py')
        result = robot.poseToMove(position[0], position[1], position[2])
        print("Goal execution done!")
