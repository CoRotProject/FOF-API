#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist
import time
import math

class MoveTurtlebot():

    def __init__(self):
        self.turtlebot_vel_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.cmd = Twist()
        self.ctrl_c = False
        rospy.on_shutdown(self.shutdownhook)
        self.rate = rospy.Rate(10)

    def publish_once_in_cmd_vel(self):
        """
        This is because publishing in topics sometimes fails the first time you publish.
        In continuous publishing systems, this is no big deal, but in systems that publish only
        once, it IS very important.
        """
        while not self.ctrl_c:
            connections = self.turtlebot_vel_publisher.get_num_connections()
            if connections > 0:
                self.turtlebot_vel_publisher.publish(self.cmd)
                rospy.loginfo("Cmd Published")
                break
            else:
                self.rate.sleep()

    def shutdownhook(self):
        # works better than the rospy.is_shut_down()
        self.stop_turtlebot()
        self.ctrl_c = True

    def stop_turtlebot(self):
        rospy.loginfo("shutdown time! Stop the robot")
        self.cmd.linear.x = 0.0
        self.cmd.angular.z = 0.0
        self.publish_once_in_cmd_vel()

    def move_x_time(self, moving_time, linear_speed=0.2, angular_speed=0.2):

        self.cmd.linear.x = linear_speed
        self.cmd.angular.z = angular_speed

        self.publish_once_in_cmd_vel()
        time.sleep(moving_time)

    def move_square(self, square_size=0):

        i = 0

        while not self.ctrl_c and i < 4:
            # Move Forward
            self.move_x_time(moving_time=square_size, linear_speed=0.2, angular_speed=0.0)
            # Turn, the turning is not affected by the length of the side we want
            self.move_x_time(moving_time=6.5, linear_speed=0.0, angular_speed=-0.225)
            i += 1

        self.stop_turtlebot()
        rospy.loginfo("######## Finished Moving in a Square")

if __name__ == '__main__':
    rospy.init_node('move_turtlebot_test', anonymous=True)
    moveturtlebot_object = MoveTurtlebot()
    try:
        moveturtlebot_object.move_square(12)
    except rospy.ROSInterruptException:
        pass
