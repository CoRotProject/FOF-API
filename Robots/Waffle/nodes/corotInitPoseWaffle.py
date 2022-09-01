#!/usr/bin/env python

#Ce node est different de poseInit.py, ici, on definit la pose en fonction de la derniere pose dans la BDD

import rospy
import quaternionTransforms
from geometry_msgs.msg import PoseWithCovarianceStamped
import Commandes.commandeAPI as commandeAPI
import time
import sys


def setPositionByDatabase(factoryid, robotId):
    robotinfo = commandeAPI.getvalues(factoryid, "robot", robotId)
    rospy.loginfo(robotinfo)
    xpos = float(robotinfo['transform2D']['x'])
    ypos = float(robotinfo['transform2D']['y'])
    theta = float(robotinfo['transform2D']['theta'])
    quaternion = quaternionTransforms.euler_to_quaternion(theta, 0, 0)

    rospy.init_node('bdd_init_pose', anonymous= True)
    pub = rospy.Publisher('initialpose', PoseWithCovarianceStamped, queue_size=10)
    msg = PoseWithCovarianceStamped()
    msg.header.frame_id = "map"
    msg.header.stamp = rospy.Time.now()
    msg.pose.pose.position.x = xpos
    msg.pose.pose.position.y = ypos
    msg.pose.pose.orientation.x = quaternion[0]
    msg.pose.pose.orientation.y = quaternion[1]
    msg.pose.pose.orientation.z = quaternion[2]
    msg.pose.pose.orientation.w = quaternion[3]
    pub.publish(msg)
    rospy.sleep(2)
    pub.publish(msg)
    rospy.sleep(2)
    pub.publish(msg)
    print("position set")

def setPositionManually(factoryid, robotId):
    robotinfo = commandeAPI.getvalues(factoryid, "robot", robotId)
    xpos = 1.253
    ypos = 10.960
    theta = quaternionTransforms.quaternion_to_euler_angle(0.713, 0, 0, 0.70)[2]

    quaternion = quaternionTransforms.euler_to_quaternion(theta, 0, 0)
    rospy.init_node('bdd_init_pose', anonymous= True)
    pub = rospy.Publisher('initialpose', PoseWithCovarianceStamped, queue_size=10)
    msg = PoseWithCovarianceStamped()
    msg.header.frame_id = "map"
    msg.header.stamp = rospy.Time.now()
    msg.pose.pose.position.x = xpos
    msg.pose.pose.position.y = ypos
    msg.pose.pose.orientation.x = quaternion[0]
    msg.pose.pose.orientation.y = quaternion[1]
    msg.pose.pose.orientation.z = quaternion[2]
    msg.pose.pose.orientation.w = quaternion[3]
    pub.publish(msg)
    rospy.sleep(2)
    pub.publish(msg)
    rospy.sleep(2)
    pub.publish(msg)
    print("position set")

if __name__ == "__main__":
    rospy.sleep(20)
    commandeAPI.seturl(sys.argv[1])
    factoryid = commandeAPI.findfactory(name=sys.argv[3])[0]
    robotId = commandeAPI.findINfactory(factoryid, "robot", name = sys.argv[2])[0]
    setPositionByDatabase(factoryid, robotId)
