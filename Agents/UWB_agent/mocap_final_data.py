
#!/usr/bin/env python

import rospy
import time
from geometry_msgs.msg import Pose


class rbot_mocap():
    def __init__(self):
       # rospy.init_node('imu_data', anonymous=True)
        self.odom_sb = rospy.Subscriber('/mocap_data', Pose, self.mocap_Callback)
        self.mocapy = Pose()
        self.flag = False
    
    def mocap_Callback(self,msg):
        # geometry_msgs/Pose pose
        self.mocapy = msg
        self.flag = True

if __name__ == '__main__':
    ex = rbot_mocap()

    try:
        while True :
            time.sleep(0.1)
            if ex.flag:
                print(ex.mocapy)
                ex.flag = False
    except rospy.ROSInterruptException:
        rospy.loginfo("node terminated.")

