#!/usr/bin/env python2
# coding: utf8
# Copyright 2018 Fabrice DUVAL

from __future__ import unicode_literals
from __future__ import print_function
import json
import time
import requests
try:
    import rospy
    from mirSupervisor.srv import GetState, SetState
    # from mirMsgs.msg import *
    ROSenable = True
except ImportError:
    ROSenable = False

MIR_Status = []

ROBOT_STATE = {"ROBOT_STATE_NONE" : 0, "ROBOT_STATE_STARTING" : 1, "ROBOT_STATE_SHUTTINGDOWN" : 2,
                "ROBOT_STATE_READY" : 3, "ROBOT_STATE_PAUSE" : 4, "ROBOT_STATE_EXECUTING" : 5,
                "ROBOT_STATE_ABORTED" : 6, "ROBOT_STATE_COMPLETED" : 7, "ROBOT_STATE_DOCKED" : 8,
                "ROBOT_STATE_DOCKING" : 9, "ROBOT_STATE_EMERGENCYSTOP" : 10, "ROBOT_STATE_MANUALCONTROL" : 11,
                "ROBOT_STATE_ERROR" : 12}
Statenb2txt = ["None", "Starting", "ShuttingDown", "Ready","Pause", "Exectuting", "Aborted", "Completed", "Docked", "Docking"]

# import actionlib
# import rospy
# from mirSupervisor.srv import *

# from lxml import etree as ET

# creation de http://mir_arm/ajax/fabrice.php?action=go_to_position&x=1.0&y=2.0&theta=90

class Mir:
    """all needed function to move mir"""
    def __init__(self, nom="mir_arm", lienhttp='http://127.0.0.1/ajax/'):
        self.mynom = nom
        self.serveur = lienhttp
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.liststatus = []
        self.initposition()

    def setready(self):
        """force ready state"""
        global ROSenable
        # permet de placer le robot en mode "ready"
        if ROSenable:
            try:
                rospy.wait_for_service('/mirsupervisor/setRobotState')
            except rospy.ServiceException:
                ROSenable = False
                return False

            try:
                service_status = rospy.ServiceProxy('/mirsupervisor/setRobotState', SetState)
                reponse = service_status(ROBOT_STATE["ROBOT_STATE_READY"])
                return reponse
            except (rospy.ServiceException, rospy.ROSException):
                print("Service call failed ")
                return False
        else:
            return False

    def go(self, point):
        """move robot"""
        query = self.serveur + "fabrice.php?action=go_to_position&x=" + str(point[0]) +"&y=" +  str(point[1]) + "&theta=" + str(point[2])
        reponse = requests.get(query)
        if reponse.status_code != 200:
            return -1
        else:
            return json.loads(reponse.text)['id']
        
    def getmission(self, id):
        """ask for mission id"""
        query = self.serveur + "mission_status.php?mission="+str(id)
        reponse = json.loads(requests.get(query).text)
        retour = {}
        retour['status'] = reponse['end_state']
        retour['message'] = reponse['message']
        retour['start_time'] = str(time.mktime(time.strptime(reponse['start_time'], '%Y-%m-%d %H:%M:%S')))
        if reponse['end_time'] == '0000-00-00 00:00:00':
            retour['end_time'] = ""
        else:
            retour['end_time'] = str(time.mktime(time.strptime(reponse['end_time'], '%Y-%m-%d %H:%M:%S')))
        retour['current_time'] =  str(time.time())
        return retour
    
    def initposition(self):
        """put position as last one"""
        query = self.serveur + "fabrice.php?action=statusliste"
        reponse = json.loads(requests.get(query).text)
        self.liststatus = [''] * len(reponse)
        for item in reponse:
            self.liststatus[int(item['state_id'])-1] = item['state']
        status = self.getstatus()   
        self.x = float(status['x'])
        self.y = float(status['y'])
        self.theta = float(status['theta'])
        return float(status['x']), float(status['y']), float(status['theta'])

    def getposition(self):
        """ask for current position"""
        query = self.serveur + "data.php"
        reponse = json.loads(requests.post(query,data={"action": "robot_position"}).text)

        return float(reponse['pos_x']), float(reponse['pos_y']), float(reponse['theta'])

    def getstatus(self):
        """get full sattus"""
        retour = {}

        retour['x'], retour['y'], retour['theta'] = self.getposition()

        query = self.serveur + "last_status.php"
        reponse = json.loads(requests.get(query).text)
        retour['map'] = reponse['map_id'] # attention, mauvaise solution
        retour['statusnumber'] = reponse['state']
        retour['status_time'] = str(time.mktime(time.strptime(reponse['time'], '%Y-%m-%d %H:%M:%S')))
        retour['current_time'] = str(time.time())
        retour['battery'] = float(reponse['battery'])

        retour['status'] = self.liststatus[int(retour['statusnumber'])-1]
        global ROSenable
        if ROSenable:
            try:
                service_status = rospy.ServiceProxy('/mirsupervisor/getRobotState', GetState)
                reponse = service_status()
                retour['rosstatus'] = [reponse.robotState, reponse.robotStateString]

            except rospy.ServiceException:
                print("Service call failed: ")
                retour['rosstatus'] = None
        else:
            retour['rosstatus'] = None
        return retour

# def rosmirstatuscallback(data):
#     global MIR_Status
#     MIR_Status = data

# #  running node to status topic if ros enable
# if ROSenable:
#     rospy.init_node('node_name')
#     rospy.Subscriber("/mir_status", MirStatus, rosmirstatuscallback)

if __name__ == "__main__":
    print("running Mir")
