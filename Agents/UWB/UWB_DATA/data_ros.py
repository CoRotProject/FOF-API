#!/usr/bin/env python

import tf
import math
import rospy
import geometry_msgs.msg
import time
from time import sleep
import csv


class mybot():
    def __init__(self, robot_name=''):
        self.frame_base = rospy.get_param('~base_frame', robot_name+'/base_link')
        self.frame_odom = rospy.get_param('~odom_frame', robot_name+'/odom')
        self.velocity_topic = rospy.get_param('~vel_topic', robot_name+'/cmd_vel')
        self.tolerance_distance = rospy.get_param('~tolerance', 0.08)
        self.speed_linear = rospy.get_param('~speed_linear', 0.4)
        self.rate_pub = rospy.get_param('~velocity_pub_rate', 10)
        self.rate = rospy.Rate(self.rate_pub)
        self.vel_pub = rospy.Publisher(self.velocity_topic,
                                       geometry_msgs.msg.Twist,
                                       queue_size=1)
        self.tf_listener = tf.TransformListener()
        rospy.on_shutdown(self.brake)
        try:
            self.tf_listener.waitForTransform(self.frame_odom,
                                              self.frame_base,
                                              rospy.Time(0),
                                              rospy.Duration(5.0))
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            rospy.logerr('tf catch exception when robot waiting for transform......')
            exit(-1)

    def move_to_target(self, dis_to_move=0):
        """
        to make robot move forward/back dis_to_move meters
        :param: dis_to_move: the distance make robot move, >0 means move forward, <0 means move back
        :type: float
        :return:
        """
        self.robot_start_pos = self.get_robot_pos_odometry()
        rospy.logdebug("****************************************************************************")
        rospy.logdebug("robot current position is x = %f, y = %f, try to move forward/back %f Meter"
                       %(self.robot_start_pos.x, self.robot_start_pos.y, dis_to_move))
        rospy.logdebug("****************************************************************************")
        while self.__is_robot_arrived(dis_to_move) is not True:
            self.__move_robot(direction=(1 if dis_to_move > 0 else -1))
            self.rate.sleep()
        self.brake()  # we have arrived the target position, so stop robot
        rospy.loginfo('arrived the target point')

    def __is_robot_arrived(self, dis_to_move):
        """
        to check has the robot arrived target position
        :param: dis_to_move: the distance thar robot needs to move forward/back
        :type: float
        :return: False --- robot has not arrived the target position
                 True --- robot has arrived the target position
        """
        robot_cur_pos = self.get_robot_pos_odometry()
        dis_moved = math.sqrt(math.pow((robot_cur_pos.x - self.robot_start_pos.x), 2) +
                                    math.pow((robot_cur_pos.y - self.robot_start_pos.y), 2))
        dis_need_move = math.fabs(dis_to_move) - dis_moved
        return False if math.fabs(dis_need_move) > self.tolerance_distance else True

    def __move_robot(self, direction=1):
        """
        send velocity to robot according to the direction
        :param: direction: when direction = 1: make robot move forward
                when direction = -1: make robot move back
        :type: int
        :return:
        """
        move_cmd = geometry_msgs.msg.Twist()
        move_cmd.linear.x = math.copysign(self.speed_linear, direction)
        self.vel_pub.publish(move_cmd)

    def get_robot_pos_odometry(self):
        """
        to get current position(x,y,z) of robot
        :return: A geometry_msgs.msg.Point type store robot's position (x,y,z)
        """
        try:
            (trans, rot) = self.tf_listener.lookupTransform(self.frame_odom,
                                                            self.frame_base,
                                                            rospy.Time(0))
        except (tf.Exception, tf.ConnectivityException, tf.LookupException):
            rospy.logerr('tf catch exception when robot looking up transform')
            exit(-1)
        return geometry_msgs.msg.Point(*trans)
    
    def create_csv_file(self):
        folder = 'TFdata.csv'
        self.f = open(folder, 'w+')
        self.f.write("x,y,z,\n")
        sleep(1)

    def get_robot_pos_tf(self):
        time.sleep(1)
        trans, rot = self.tf_listener.lookupTransform('/map','/base_link',rospy.Time(0))
        trans_to_uwbR = trans
        #trans_to_uwbR[0] = (trans[0] + 1.251-0.25)*100
        #trans_to_uwbR[1] = (trans[1] - 2.447)*100
        trans_to_uwbR[0] = (trans[0] + 1.251-0.25+0.52)*100
        trans_to_uwbR[1] = (trans[1] - 2.447-0.10)*100

        return trans
    def store_tf_ros_data(self,folder):
        val = str(self.get_robot_pos_tf())
        folder.write(val+"\n")


    def brake(self):
        """
        send command to stop the robot
        :return:
        """
        self.vel_pub.publish(geometry_msgs.msg.Twist())


if __name__ == '__main__':
    rospy.init_node('robot_main_code')
    #t_dis = rospy.get_param('~t_dis', 0.0)
    #if t_dis == 0.0:
    #    rospy.logerr('no target distance set!')
    #    exit(-1)
    #rospy.loginfo('try to move %f meters'%t_dis)
    turtlebot = mybot()
    name = 'TFdata.csv'
    x = []
    y = []
    myfile = open(name, 'w+')
    try:
        while True:
            print(turtlebot.get_robot_pos_tf())
            val = turtlebot.get_robot_pos_tf()
            x.append(int(val[0]))
            y.append(int(val[1]))
            rows = zip(x, y)
            with open(name, "w") as f:
                writer = csv.writer(f)
                for row in rows:
                    writer.writerow(row)   
    except KeyboardInterrupt:
        
        pass

