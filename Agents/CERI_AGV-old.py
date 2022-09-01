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

modedebug = True

WAFFLE_Status = ["offline", "free", "ShuttingDown", "internalprocess", "busy", "error"]

class CERI_AGV:
    def __init__(self, nom):
        self.mynom = nom
        self.x = 999.999
        self.y = 999.999
        self.theta = 0.0
        self.beforemovex = 999.999
        self.beforemovey = 999.999
        self.beforemovetheta = 0.0
        self.liststatus = []
        self.status = "internalprocess"
        #self.jesuispret()
        self.battery = 100.0
        # creation d'un nom de node
        self.node = rospy.init_node('SequencerAgent', anonymous=False)
        self.temp0 = rospy.Time.now()
        # connexion lien vers pose_listener
        self.pose_sub = rospy.Subscriber('/vikiloc/pose', PoseWithCovarianceStamped, self.pose_listener)
        self.initpos = rospy.Publisher('initialpose', PoseWithCovarianceStamped, queue_size=10)
        self.clientmove_base = actionlib.SimpleActionClient('move_base',MoveBaseAction)
        self.clientmove_base.wait_for_server()
        # initialisation goal vierge
        self.goal = MoveBaseGoal()
        # self.goal.target_pose.header.frame_id = "map"
        self.goal.target_pose.header.frame_id = "odom"
        self.status ="free"

    #def jesuispret(self):
    #    rospy.init_node('verifwaffleready', anonymous = True)
    #    data = rospy.wait_for_message('verif_ready', String, timeout=20)
    #    print(data)

    def initposition(self, point):
        quaternion = quaternionTransforms.euler_to_quaternion(quaternionTransforms.angleToRad(point[2]),0,0)
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = "map"
        msg.header.stamp = rospy.Time.now()
        msg.pose.pose.position.x = point[0]
        msg.pose.pose.position.y = point[1]
        msg.pose.pose.orientation.x = quaternion[0]
        msg.pose.pose.orientation.y = quaternion[1]
        msg.pose.pose.orientation.z = quaternion[2]
        msg.pose.pose.orientation.w = quaternion[3]
        self.initpos.publish(msg)
        rospy.sleep(2)
        self.initpos.publish(msg)
        rospy.sleep(2)
        self.initpos.publish(msg)
        print("position (re)set to {0[0]},{0[1]},{0[2]}°".format(point))

        #self.x, self.y, self.theta = poseInit.initialLocate()
        rospy.loginfo("position (re)set to {0[0]},{0[1]},{0[2]}°".format(point))
        #pose2DSET.newPosition(self.x, self.y, self.theta, self.node)
        
        #for i in range(10):
        #    poseInit.calibrer()

    def callback_active(self, ):
        print("Go")
        self.status = "busy"
    
    def callback_feedback(self, feedback):
        currentx = feedback.base_position.pose.position.x
        currenty = feedback.base_position.pose.position.x
        currenttheta = feedback.base_position.pose.orientation
        currenttheta = quaternionTransforms.quaternion_to_euler(currenttheta.x, currenttheta.y, currenttheta.z, currenttheta.w, )

        deltax = self.beforemovex - currentx
        deltay = self.beforemovey - currenty
        deltatheta = self.beforemovetheta - currenttheta
        deltatime = rospy.Time.now() - self.beforemovetime

        if modedebug:
            print("feedback:{}".format(str(feedback)))
            print("DX, DY, DTheta, Dtime = {}, {}, {}, {}".format(deltax, deltay, deltatheta, deltatime))
        else:
            print(".", end = "")

    def callback_done(self, state, result):
        self.status = "done"
        if modedebug:
            print("state:{} ; result:{}".format(str(state),str(result)))
        else:
            print("result OK")

    def poseToMove(self, x, y, YawDegres):
        self.status = "internalprocess"
        #transformation de l angle en yaw en quaternion
        quaternion = quaternionTransforms.euler_to_quaternion(quaternionTransforms.angleToRad(YawDegres),0,0)

        # client = actionlib.SimpleActionClient('move_base',MoveBaseAction)
        # client.wait_for_server()

        # #remplissage de l objet goal, pour l'envoyer par la suite (les valeurs non precisees sont par defaut a 0)
        # goal = MoveBaseGoal()
        # goal.target_pose.header.frame_id = "map"
        self.goal.target_pose.header.stamp = rospy.Time.now()
        self.goal.target_pose.pose.position.x = x
        self.goal.target_pose.pose.position.y = y
        self.goal.target_pose.pose.orientation.z = quaternion[2]
        self.goal.target_pose.pose.orientation.w = quaternion[3]

        self.beforemovex = self.x
        self.beforemovey = self.x
        self.beforemovetheta = self.theta
        self.beforemovetime = rospy.Time.now()
        self.clientmove_base.send_goal(self.goal,
                active_cb=self.callback_active,
                feedback_cb=self.callback_feedback,
                done_cb=self.callback_done)

        # client.send_goal(goal)
        # wait = client.wait_for_result()
        # if not wait:
        #     rospy.logerr("Action server not available!")
        #     rospy.signal_shutdown("Action server not available!")
        # else:
        #     return client.get_result()

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

    def pose_listener(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        _, _, theta = quaternionTransforms.quaternion_to_euler( [ msg.pose.pose.orientation.x, msg.pose.pose.orientation.y, msg.pose.pose.orientation.z, msg.pose.pose.orientation.w ] )
        self.theta = quaternionTransforms.angleToDeg(theta)

    def getposition(self):
        return self.x, self.y, self.theta

    # def currentLocation(self):
    #     #rospy.init_node('amcl_pose_listener',anonymous=True)
    #     time.sleep(0.05)
    #     rospy.wait_for_service('request_nomotion_update', timeout=5)
    #     rospy.ServiceProxy('request_nomotion_update', Empty )()
    #     time.sleep(0.1)
    #     data = rospy.wait_for_message('amcl_pose',PoseWithCovarianceStamped , timeout=None)
    #     #on transforme le quaternion pour l avoir en degrees theta
    #     angle = quaternionTransforms.quaternion_to_euler_angle(data.pose.pose.orientation.w, 0, 0, data.pose.pose.orientation.z)
    #     return data.pose.pose.position.x, data.pose.pose.position.y, angle[2]

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
        try:
            # rospy.init_node('movebase_client_py')
            result = robot.poseToMove(position[0], position[1], position[2])
            if result:
                rospy.loginfo("Goal execution done!")
        except rospy.ROSInterruptException:
            rospy.loginfo("Navigation test finished.")