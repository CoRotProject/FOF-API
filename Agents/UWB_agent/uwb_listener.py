import rospy
from std_msgs.msg import String
import time

class uwb_listener():
    def __init__(self):
        #rospy.init_node('uwb_listener', anonymous=False)
        self.tf = rospy.Subscriber('data_uwb_pos', String, self.tf_Callback)
        self.datasub = String()
        self.flag = False
        self.out=[0,0]

    def tf_Callback(self,pose_message):
        self.datasub.data = pose_message.data.strip(' \r\n')
        val = self.datasub.data.split(',')
        if len(val)==6:
            self.out =  [val[1],val[2]]
        self.flag = True


if __name__ == '__main__':
    ex = uwb_listener()
    try:
        while True :
            time.sleep(0.1)
            if ex.flag:
                print(ex.out)
                ex.flag = False
    except rospy.ROSInterruptException:
        rospy.loginfo("node terminated.")
