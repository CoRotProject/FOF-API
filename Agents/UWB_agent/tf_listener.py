import rospy
from geometry_msgs.msg import Point
import time

class tf_listener():
    def __init__(self):
       # rospy.init_node('tf_listener', anonymous=False)
        self.tf = rospy.Subscriber('position_tf', Point, self.tf_Callback)
        self.datasub = Point()
        self.flag = False

    def tf_Callback(self,pose_message):
        self.datasub.x = pose_message.x
        self.datasub.y = pose_message.y
        self.datasub.z  = pose_message.z
        self.flag = True


if __name__ == '__main__':
    ex = tf_listener()
    try:
        while True :
            time.sleep(0.1)
            if ex.flag:
                print(ex.datasub)
                ex.flag = False
    except rospy.ROSInterruptException:
        rospy.loginfo("node terminated.")
