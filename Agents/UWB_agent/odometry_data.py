#!/usr/bin/env python2

import rospy
import time
from nav_msgs.msg import Odometry



class rbot_odometry():
    def __init__(self):
        rospy.init_node('odometry_data', anonymous=True)
        self.odom_sb = rospy.Subscriber('/odom', Odometry, self.odom_Callback)
        self.turtlebot_odom_pose = Odometry()
        self.flag = False
    
    def odom_Callback(self,pose_message):
        # geometry_msgs/Pose pose
        self.turtlebot_odom_pose.pose.pose.position.x = pose_message.pose.pose.position.x
        self.turtlebot_odom_pose.pose.pose.position.y = pose_message.pose.pose.position.y
        self.turtlebot_odom_pose.pose.pose.position.z  = pose_message.pose.pose.position.z

        self.turtlebot_odom_pose.pose.pose.orientation.w=pose_message.pose.pose.orientation.w
        self.turtlebot_odom_pose.pose.pose.orientation.x=pose_message.pose.pose.orientation.x
        self.turtlebot_odom_pose.pose.pose.orientation.y=pose_message.pose.pose.orientation.y
        self.turtlebot_odom_pose.pose.pose.orientation.z=pose_message.pose.pose.orientation.z
        self.flag = True
        # rospy.loginfo(" x:" + str(self.turtlebot_odom_pose.pose.pose.position.x ) + " y:" +
        #               str(self.turtlebot_odom_pose.pose.pose.position.y) +"z:"+
        #                str(self.turtlebot_odom_pose.pose.pose.position.z))
        # rospy.loginfo("theta : " + str (self.turtlebot_odom_pose.pose.pose.orientation.z))


        
if __name__ == '__main__':
    ex = rbot_odometry()

    try:
        while True :
            time.sleep(0.1)
            if ex.flag:
                print(ex.turtlebot_odom_pose.pose.pose)
                ex.flag = False
    except rospy.ROSInterruptException:
        rospy.loginfo("node terminated.")
