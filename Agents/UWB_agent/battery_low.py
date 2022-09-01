
import rospy
import roslib
from std_msgs.msg import Bool, Float32
import time
# found from grepping /opt/ros/indigo that the message was sensor_msgs.msg/BatteryState
# but the p2os driver said differently in the error output
from sensor_msgs.msg import BatteryState

battery_threshold = 11.2 # volts
pub = None

def battery_callback(msg):
    #rospy.loginfo(msg)
    #print(msg.voltage)
    #pub.publish(True)
    if msg.voltage < battery_threshold:
      pub.publish(True)
    else:
      pub.publish(False)

def main():
    global pub

    rospy.init_node('battery_monitor')

    rospy.Subscriber('battery_state', BatteryState, battery_callback)

    pub = rospy.Publisher('battery_low', Bool, queue_size=1)

    rospy.spin()


if __name__ == '__main__':
    main()
