#!/usr/bin/env python2

import rospy
import time
from std_msgs.msg import Bool



class battery():
    def __init__(self):
        #rospy.init_node('battery_is_low', anonymous=True)
        self.battery_sb = rospy.Subscriber('/battery_low', Bool, self.battery_Callback)
        self.battery_is_low = False
        self.stop_me = False
        self.pub = rospy.Publisher('/stop_me', Bool, queue_size=1)

    def battery_Callback(self,msg):
        self.battery_is_low = msg.data
        #self.pub.publish(True)
        #print('test')
        if self.stop_me:
           self.pub.publish(True)
           #self.stop_me = False
        else:
            self.pub.publish(False)



if __name__ == '__main__':
    ex = battery()

    try:
        while True :
            time.sleep(0.1)
            #print(ex.battery_is_low)
    except rospy.ROSInterruptException:
        rospy.loginfo("node terminated.")

