#!/usr/bin/env python

import rospy
import time
from sensor_msgs.msg import Imu



class rbot_imu():
    def __init__(self):
        #rospy.init_node('imu_data', anonymous=True)
        self.odom_sb = rospy.Subscriber('/imu', Imu, self.imu_Callback)
        self.turtlebot_imu = Imu()
        self.flag = False
    
    def imu_Callback(self,msg):
        # geometry_msgs/Pose pose
        self.turtlebot_imu.orientation = msg.orientation
        self.flag = True

if __name__ == '__main__':
    ex = rbot_imu()

    try:
        while True :
            time.sleep(0.1)
            if ex.flag:
                print(ex.turtlebot_imu.orientation)
                ex.flag = False
    except rospy.ROSInterruptException:
        rospy.loginfo("node terminated.")

