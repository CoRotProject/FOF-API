#!/usr/bin/env python
import time, serial, rospy
from tf import TransformBroadcaster
from FOF_API.Agents.mir_api.mir_utils import mymir
import serial
import requests
import operator
#MirIp = '10.191.76.55'
#mir_arm = mymir(MirIp)
#offset=(3.619+1.01,-7.122+0.05,0)
device_port = "/dev/ttyACM0"

class UwbXyzPublisher(object):
    def __init__(self):
        rospy.init_node("iidre_uwb_xyz_publisher")
        self.tfb = TransformBroadcaster()
        self.serial = None
        self.device_name = rospy.get_param("name", "uwb")
        self.device_port = rospy.get_param("port", "/dev/ttyACM0")
        self.device_frame_id = rospy.get_param("frame_id", "map")
        self.publish_anchors = rospy.get_param("publish_anchors", True)
    
    def connect(self):
        if self.serial is not None:
            try:
                self.serial.close()
            except:
                pass
        
        rospy.loginfo("Connecting to {}...".format(self.device_port))
        self.serial = serial.Serial(self.device_port)
        rospy.loginfo("Connected! Now publishing tf frame '{}' in frame '{}'...".format(self.device_name, self. device_frame_id))

    def run(self):
        while not rospy.is_shutdown():
            line = str(self.serial.readline())
            self.parse_and_publish(line)
            #print(line)
            
                

    def parse_and_publish(self, line):
        fb = line
        #print(fb)
        fb_cmd = fb[0:5]
        fb_data = fb[6:-1].replace("\r\n","").split(",")
        time = fb_data[0]
        if fb_cmd == "+DPOS":
            # This is usable even if the device has not been preconfigured with the uwbSupervisor
            # Just triangulate the distance (not done here)
            #print(fb_data)
            anchor_id = fb_data[5]
            anchor_dist = fb_data[9]
            anchor_xyz = fb_data[6:9]
            ax_m, ay_m, az_m = map(lambda x: float(x)/100, anchor_xyz)

            if self.publish_anchors:
                self.tfb.sendTransform(
                    (ax_m, ay_m, az_m), (0, 0, 0, 1),   # device position, quaternion
                    rospy.Time.now(),
                    anchor_id,
                    self.device_frame_id)  

        if fb_cmd == "+DPOS":
            # This is usable even if the device has not been preconfigured with the uwbSupervisor
            # Just triangulate the distance (not done here)
            robot_id = fb_data[1]
            #anchor_dist = fb_data[2]
            anchor_xyz = fb_data[2:5]
            ax_m, ay_m, az_m = map(lambda x: float(x)/100, anchor_xyz)

            if self.publish_anchors and (robot_id == "4D144137" or robot_id == "D141C33" or robot_id == "D02D092" or robot_id == "4D025C9F"):
                #mir_pos_related_to_anchor1= tuple(map(operator.add, mir_arm.getposition(), offset))
                #mir_pos_related_to_anchor1 =  tuple(map(operator.mul,mir_pos_related_to_anchor1,(100,100,100)))
                #print(anchor_xyz,"  ",mir_pos_related_to_anchor1)
                self.tfb.sendTransform(
                    (ax_m, ay_m, az_m), (0, 0, 0, 1),   # device position, quaternion
                    rospy.Time.now(),
                    robot_id,
                    self.device_frame_id)  
            
            
        if fb_cmd == "+DIST":
            # This is usable even if the device has not been preconfigured with the uwbSupervisor
            # Just triangulate the distance (not done here)
            anchor_id = fb_data[1]
            anchor_dist = fb_data[2]
            anchor_xyz = fb_data[3:6]
            ax_m, ay_m, az_m = map(lambda x: float(x)/100, anchor_xyz)

            if self.publish_anchors:
                self.tfb.sendTransform(
                    (ax_m, ay_m, az_m), (0, 0, 0, 1),   # device position, quaternion
                    rospy.Time.now(),
                    anchor_id,
                    self.device_frame_id)   
        
        elif fb_cmd == "+MPOS":
            # This is usable if device has been preconfigured with the uwbSupervisor
            x, y, z = fb_data[1:4]
            # Convert from centimeters (in the JSON infra file) to meters
            x_m, y_m, z_m = map(lambda x: float(x)/100, [x, y, z])

            self.tfb.sendTransform(
                (x_m, y_m, z_m), (0, 0, 0, 1),   # device position, quaternion
                rospy.Time.now(),
                self.device_name,
                self.device_frame_id)

if __name__ == "__main__":
    node = UwbXyzPublisher()
    node.connect()
    node.run()
