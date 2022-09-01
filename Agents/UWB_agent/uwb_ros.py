#!/usr/bin/env python
import rospy
import serial
from std_msgs.msg import String
import time


class Uwb_reader:

    def __init__(self):
        rospy.init_node('uwb_reader', anonymous=True, disable_signals=True)
        self.serial_port = '/dev/ttyACM1'
        topic_name = 'data_uwb_pos'
        self.ser = None

        self.pub = rospy.Publisher(topic_name, String, queue_size=1)
        rospy.on_shutdown(self.close_serial_if_active)

    def close_serial_if_active(self):
        if(not(self.ser == None)):
            self.ser.close()
        
    def start_reading(self):
        while not rospy.is_shutdown():
            try:
                if(self.ser == None):
                    rospy.loginfo("Trying to reconnect to serial")
                    self.ser = serial.Serial(self.serial_port, 115200, timeout=1, xonxoff=True)
                    rospy.loginfo("Connected to serial")
                    time.sleep(1)
                    self.ser.reset_input_buffer()
                    self.ser.reset_output_buffer()

                ser_bytes = self.ser.readline()

                if(ser_bytes):
		            #val = str(ser_bytes.decode().strip(' \r\n'))
                    #print(val)
                    if ser_bytes.startswith('+MPOS:'):         
                        self.pub.publish(ser_bytes)

                else:
                    rospy.logwarn("Serial timeout occured")

            except serial.serialutil.SerialException:
                if(not(self.ser == None)):
                    self.ser.close()
                    self.ser = None
                    rospy.logwarn("Disconnecting from serial")
                    rospy.logwarn("Serial disconnected")
                    time.sleep(0.25)


if __name__ == '__main__':
    uwb_reader = Uwb_reader()
    uwb_reader.start_reading()