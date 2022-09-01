#!/usr/bin/env python
# BEGIN ALL
import rospy, cv2, cv_bridge, numpy
from sensor_msgs.msg import Image, CompressedImage
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
import time
import threading
import numpy as np
class Follower:
  def __init__(self):
    self.bridge = cv_bridge.CvBridge()
    #cv2.namedWindow("window", 1)
    self.lock = threading.Lock()
    self.image_sub = rospy.Subscriber('/raspicam_node/image', 
                                      Image, self.image_callback)
    self.cmd_vel_pub = rospy.Publisher('cmd_vel',
                                       Twist, queue_size=1)
    self.twist = Twist()
    self.stopper = False
    self.battery_sub = rospy.Subscriber('/stop_me',Bool,self.stopper_callback)
    self.h = 960
    self.w = 1280

  def stopper_callback(self,msg):
       self.stopper = msg.data
       #print(msg)
  def image_callback(self, msg):
    #print('start')
    self.lock.acquire()
    image = self.bridge.imgmsg_to_cv2(msg,desired_encoding='bgr8')
    #image = self.bridge.imgmsg_to_cv2(msg)
    #np_arr = np.fromstring(msg.data, np.uint8)
    #image = cv2.imdecode(np_arr ,cv2.IMREAD_COLOR )
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    #normal
    lower_yellow = numpy.array([0,  120,  95])
    upper_yellow = numpy.array([255, 255, 255])
    #compessed
    #lower_yellow = numpy.array([0,  0,  121])
    #upper_yellow = numpy.array([94, 255, 255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    h = self.h
    w = self.w
    search_top = 3*h/4
    search_bot = 3*h/4 + 20
    mask[0:search_top, 0:w] = 0
    mask[search_bot:h, 0:w] = 0
    M = cv2.moments(mask)
    if M['m00'] > 0:
      cx = int(M['m10']/M['m00'])
      cy = int(M['m01']/M['m00'])
      #cv2.circle(image, (cx, cy), 20, (0,0,255), -1)
      # BEGIN CONTROL
      err = cx - w/2
      self.twist.linear.x = 0.15
      self.twist.angular.z = -float(err) / 2125
      self.cmd_vel_pub.publish(self.twist)
    #print(self.stopper)
    if self.stopper:
       print('stop')
       cmd = Twist()
       cmd.linear.x = 0.0
       cmd.angular.z = 0.0
       self.cmd_vel_pub.publish(cmd)
       time.sleep(180)
       # END CONTROL
    # cv2.imshow("window", image)
    #cv2.waitKey(3)
    self.lock.release()

rospy.init_node('follower')
#time.sleep(10)
follower = Follower()
rospy.spin()
# END ALL
