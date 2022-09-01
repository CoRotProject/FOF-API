import rospy
import time
from mirMsgs.msg import *

toto=[]
runflag = True


def listener():
    rospy.init_node('node_name')
    rospy.Subscriber("/mir_status", MirStatus, callback)
#    rospy.spin()


def callback(data):
    global toto
    global runflag
    runflag = False
    toto = data

while runflag:
    listener()
#    time.sleep(1)

print(toto)
