#!/usr/bin/env python
from __future__ import unicode_literals
from __future__ import print_function
import json
import time
# import requests

import rospy
import actionlib
from std_msgs.msg import String
from std_srvs.srv import Empty
from geometry_msgs.msg import PoseWithCovarianceStamped
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import quaternionTransforms

WAFFLE_Status = ["offline", "free", "ShuttingDown", "internalprocess", "busy", "error"]

class Waffle:
    def __init__(self, nom):
        self.mynom = nom
        self.x = 1.253
        self.y = 10.960
        self.theta = quaternionTransforms.quaternion_to_euler_angle(0.713, 0, 0, 0.70)[2]
        self.liststatus = []
        self.node = rospy.init_node('WaffleAgent')
        self.status = "internalProcess"
        #self.jesuispret()
        self.status ="free"


    #def jesuispret(self):
    #    rospy.init_node('verifwaffleready', anonymous = True)
    #    data = rospy.wait_for_message('verif_ready', String, timeout=20)
    #    print(data)

    def initposition(self):
        #self.x, self.y, self.theta = poseInit.initialLocate()
        rospy.loginfo("try new position")
        #pose2DSET.newPosition(self.x, self.y, self.theta, self.node)
        
        #for i in range(10):
        #    poseInit.calibrer()
    
    def poseToMove(self, x, y, Yaw):
        #transformation de l angle en yaw en quaternion
        quaternion = quaternionTransforms.euler_to_quaternion(Yaw,0,0)

        client = actionlib.SimpleActionClient('move_base',MoveBaseAction)
        client.wait_for_server()

        #remplissage de l objet goal, pour l'envoyer par la suite (les valeurs non precisees sont par defaut a 0)
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = x
        goal.target_pose.pose.position.y = y
        goal.target_pose.pose.orientation.z = quaternion[2]
        goal.target_pose.pose.orientation.w = quaternion[3]

        client.send_goal(goal)
        wait = client.wait_for_result()
        if not wait:
            rospy.logerr("Action server not available!")
            rospy.signal_shutdown("Action server not available!")
        else:
            return client.get_result()

    def go(self, point):
        """move robot"""
        self.status = "busy"
        #query = self.serveur + "fabrice.php?action=go_to_position&x=" + str(point[0]) +"&y=" +  str(point[1]) + "&theta=" + str(point[2])
        try:
            result = self.poseToMove(point[0],point[1],point[2])
            if result:
                rospy.loginfo("Goal execution done!")
                self.status = "free"
        except rospy.ROSInterruptException:
            rospy.loginfo("Navigation test finished.")
            self.status = "error"

        #reponse = requests.get(query)
        #if reponse.status_code != 200:
        #    return -1
        #else:
        #    return json.loads(reponse.text)['id']

    def getposition(self):
        self.x, self.y, self.theta = self.currentLocation()
        return self.x, self.y, self.theta

    def currentLocation(self):
        #rospy.init_node('amcl_pose_listener',anonymous=True)
        time.sleep(0.05)
        rospy.wait_for_service('request_nomotion_update', timeout=5)
        rospy.ServiceProxy('request_nomotion_update', Empty )()
        time.sleep(0.1)
        data = rospy.wait_for_message('amcl_pose',PoseWithCovarianceStamped , timeout=None)
        #on transforme le quaternion pour l avoir en degrees theta
        angle = quaternionTransforms.quaternion_to_euler_angle(data.pose.pose.orientation.w, 0, 0, data.pose.pose.orientation.z)
        return data.pose.pose.position.x, data.pose.pose.position.y, angle[2]

    def getstatus(self):
        """get full sattus"""
        retour = {}
        retour['x'], retour['y'], retour['theta'] = self.getposition()
        retour['status'] = self.status
        return retour

if __name__ == '__main__':
    robot = Waffle("waffle_03")
    position = [int(input("entrez la position en x : ")), int(input("entrez la position en y : ")), int(input("entrez la rotation : "))]
    try:
        rospy.init_node('movebase_client_py')
        result = robot.poseToMove(position[0], position[1], position[2])
        if result:
            rospy.loginfo("Goal execution done!")
    except rospy.ROSInterruptException:
        rospy.loginfo("Navigation test finished.")