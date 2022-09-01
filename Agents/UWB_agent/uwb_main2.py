import sys
import time
from FOF_API.Agents.UWB_agent.odometry_data import rbot_odometry
from FOF_API.Agents.UWB_agent.battery_data import battery
from FOF_API.Agents.UWB_agent.tf_listener import tf_listener
from FOF_API.Agents.UWB_agent.uwb_listener import uwb_listener
from FOF_API.Agents.UWB_agent.imu_data import rbot_imu
from FOF_API.Agents.UWB_agent.mocap_data import Mocap
from FOF_API.MOCAP.getrigidbody import NatNetClient
import csv
import math
import threading


class trajectory_timer(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.release = True
            self.running = True
            self.temp = False
        def releaser(self):
            self.temp = True
        def run(self):
            while self.running:
                  time.sleep(0.1)
                  if self.temp:
                     self.release = False
                     time.sleep(30)
                     self.release = True
                     self.temp = False
        def terminate(self):
            self.running = False

def euler_from_quaternion(x, y, z, w):
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)

        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)

        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)

        return math.degrees(roll_x), math.degrees(pitch_y), math.degrees(yaw_z) # in radians
if __name__ == "__main__":
    '''Mocap config'''
    '''Mocap config'''
    optionsDict = {}
    optionsDict["clientAddress"] = "10.191.76.66"
    optionsDict["serverAddress"] = "10.191.76.176"
    optionsDict["use_multicast"] = False

    streaming_client = NatNetClient()
    streaming_client.set_client_address(optionsDict["clientAddress"])
    streaming_client.set_server_address(optionsDict["serverAddress"])
    streaming_client.set_use_multicast(optionsDict["use_multicast"])

    # Configure the streaming client to call our rigid body handler on the emulator to send data out.
    mymocap = Mocap(optionsDict["clientAddress"],optionsDict["serverAddress"])
    streaming_client.new_frame_listener = mymocap.receive_new_frame
    streaming_client.rigid_body_listener = mymocap.receive_rigid_body_frame
    streaming_client.set_print_level(0)

    # Start up the streaming client now that the callbacks are set up.
    # This will run perpetually, and operate on a separate thread.
    is_running = streaming_client.run()
    if not is_running:
        print("ERROR: Could not start streaming client.")
        try:
            sys.exit(1)
        except SystemExit:
            print("...")
        finally:
            print("exiting")
    time.sleep(1)
    if streaming_client.connected() is False:
        print("ERROR: Could not connect properly.  Check that Motive streaming is on.")
        try:
            sys.exit(2)
        except SystemExit:
            print("...")
        finally:
            print("exiting")

    streaming_client.get_infos()
    time.sleep(1)
    # ultra wideband

    writer = open('All_data.csv', 'w+')
    writer.write("x_uwb,y_uwb,x_odom,y_odom,tf_x,tf_y,mocap_x,mocap_y,mocap_q_x,mocap_q_y,mocap_q_z,mocap_q_w,\n")
    tf_lis = tf_listener()
    uwb_lis = uwb_listener()
    ex = rbot_odometry()
    imu = rbot_imu()
    mybattery = battery()
    time.sleep(0.1)
    try:
        print('start')
        trajectory = 0
        trajectory_release = trajectory_timer()
        trajectory_release.start()
        while True:
            time.sleep(0.1)
            if ex.flag:

              odom_x = ex.turtlebot_odom_pose.pose.pose.position.x
              odom_y = ex.turtlebot_odom_pose.pose.pose.position.y
              tf_x=tf_lis.datasub.x
              tf_y=tf_lis.datasub.y
              uwb=uwb_lis.out
              ex.flag = False
              mocap_pos  = mymocap.get_body_frame()[13][0]
              mocap_quat = mymocap.get_body_frame()[13][1]
            if not mybattery.battery_is_low:
               mybattery.stop_me = False
            #print(trajectory_release.release)
            if (149<=mocap_pos[0]*100<=155)and(-120<mocap_pos[1]*100<-99) and trajectory_release.release:
              trajectory_release.releaser()
              trajectory = trajectory+1
              print(trajectory)
              if mybattery.battery_is_low:
                 mybattery.stop_me = True
                 print('stop')
            with open("All_data.csv","a") as f:
                writer = csv.writer(f,delimiter=",")
                writer.writerow([uwb[0],uwb[1],odom_x*100,odom_y*100,\
                       tf_x,tf_y,mocap_pos[0]*100,\
                            mocap_pos[1]*100,mocap_pos[2]*100,mocap_quat[0],mocap_quat[1],mocap_quat[2],mocap_quat[3],\
                                     imu.turtlebot_imu.orientation.x,imu.turtlebot_imu.orientation.y,\
                                            imu.turtlebot_imu.orientation.z,\
                                                 imu.turtlebot_imu.orientation.w,trajectory])
                f.close

    except (KeyboardInterrupt, SystemExit):
        print("killed")

    print("exiting")

