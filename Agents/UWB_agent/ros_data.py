#!/usr/bin/env python2

import rospy
import time
from rospy.timer import sleep
import tf
from geometry_msgs.msg import Point


class dataros:
    def __init__(self):
        rospy.init_node('get_data_ros')
        self.listener = tf.TransformListener()
        self.publisher_tf =rospy.Publisher('position_tf', Point, queue_size = 1)
        self.datapub = Point()
        sleep(1)
    def run(self):   
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            trans, _ = self.listener.lookupTransform('/map','/base_link',rospy.Time(0))
            trans_to_uwbR = trans
            #la transforme de est a verifier
            trans_to_uwbR[0] = (trans[0])*100
            trans_to_uwbR[1] = (trans[1])*100
            self.datapub.x = trans_to_uwbR[0]
            self.datapub.y = trans_to_uwbR[1]
            self.datapub.z = 0
            self.publisher_tf.publish(self.datapub)
            rate.sleep()
        
        return trans_to_uwbR[0:2]
if __name__ == '__main__':
    ex = dataros()
    try:
        ex.run()
    except (KeyboardInterrupt, SystemExit):
        pass
