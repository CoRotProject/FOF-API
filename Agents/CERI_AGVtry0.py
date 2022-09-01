#!/usr/bin/env python
# coding: utf-8

import rospy
import time
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import PoseWithCovarianceStamped
import math
from quaternionTransforms import euler_to_quaternion, quaternion_to_euler

import Commandes.commandeAPI as commandeAPI

nomfactory = "Factory CERI"
nomrobot = "CERI_AGV"
agvceri = ""

def pose_listener(msg):
    global factoryid
    global agvceri
    x = msg.pose.pose.position.x
    y = msg.pose.pose.position.y
    Roll, Pitch, Yaw = quaternion_to_euler( [ msg.pose.pose.orientation.x, msg.pose.pose.orientation.y, msg.pose.pose.orientation.z, msg.pose.pose.orientation.w ] )

    # TODO : Détecter mouvement et ne pas mettre à jour si petit déplacement et/ou 1fois/sec
    commandeAPI.updateobject(factoryid, "robot", agvceri, {"transform2D":{"x":x,"y":y,"theta":Yaw}})

def pub_destination(x,y,Rz):
    """
        Publie une destination
            x : position X (m)
            y : position Y (m)
            Rz : rotation Z (deg)
    """
    dest = PoseStamped()
    dest.header.stamp = rospy.Time.now()
    dest.header.frame_id = "factory"
    dest.pose.position.x = x
    dest.pose.position.y = y

    q = euler_to_quaternion(0, 0,math.radians(Rz))
    dest.pose.orientation.x = q[0]
    dest.pose.orientation.y = q[1]
    dest.pose.orientation.z = q[2]
    dest.pose.orientation.w = q[3]

    destination_pub.publish( dest )
    
if __name__ == '__main__':
    rospy.init_node('sequencer', anonymous=True)
    destination_pub = rospy.Publisher('sequencer/destination', PoseStamped, queue_size=10)
    pose_sub = rospy.Subscriber('/vikiloc/pose', PoseWithCovarianceStamped, pose_listener)

    # FOF-API intialization
    commandeAPI.seturl("http://192.168.32.100:5000/")
    try:
        factoryid = commandeAPI.findfactory(name=nomfactory)[0]
    except IndexError:
        rospy.logfatal("Base inacessible. Pause puis quitte")
        exit("Base non valide")

    try:
        agvceri = commandeAPI.findINfactory(factoryid,"robot", name=nomrobot)[0]
    except IndexError:
        rospy.logfatal("robot {} inacessible. Pause puis quitte".format(nomrobot))
        exit("Robot non valide")

    robot = commandeAPI.getvalues(factoryid, "robot", agvceri)
    #Lastpos = [robot['transform2D']['x'], robot['transform2D']['y'], robot['transform2D']['theta'], ] # x, y, Theta

    try :
        #rospy.loginfo("Starting")

        while not rospy.is_shutdown():

            # TODO : récupérer destinations dans la BDD et publier avec fonction pub_destination
            pub_destination( 1,2,3 ) # exemple
            rospy.sleep(2) # TODO : supprimer

    except rospy.ROSInterruptException: pass
