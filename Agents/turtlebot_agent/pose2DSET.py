#!/usr/bin/env python
import rospy
import quaternionTransforms
from geometry_msgs.msg import PoseWithCovarianceStamped

def newPosition(xpos, ypos, angle, node):
    quaternion = quaternionTransforms.euler_to_quaternion(angle, 0, 0)
    #rospy.init_node('pub_position_node', anonymous=True)
    pub = rospy.Publisher('initialpose', PoseWithCovarianceStamped, queue_size=10)
    msg = PoseWithCovarianceStamped()
    msg.header.frame_id = "map"
    msg.header.stamp = rospy.Time.now()
    msg.pose.pose.position.x = xpos
    msg.pose.pose.position.y = ypos
    msg.pose.pose.orientation.z = quaternion[2]
    msg.pose.pose.orientation.w = quaternion[3]
    pub.publish(msg)
    rospy.loginfo("pose 2D set")
