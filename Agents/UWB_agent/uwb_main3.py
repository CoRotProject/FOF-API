import time
from FOF_API.Agents.UWB_agent.odometry_data import rbot_odometry
from FOF_API.Agents.UWB_agent.battery_data import battery
from FOF_API.Agents.UWB_agent.tf_listener import tf_listener
from FOF_API.Agents.UWB_agent.uwb_listener import uwb_listener
from FOF_API.Agents.UWB_agent.imu_data import rbot_imu
from FOF_API.Agents.UWB_agent.mocap_final_data import rbot_mocap
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

        return math.degrees(roll_x), math.degrees(pitch_y), math.degrees(yaw_z) 
if __name__ == "__main__":

    writer = open('All_data.csv', 'w+')
    writer.write("x_uwb,y_uwb,x_odom,y_odom,tf_x,tf_y,mocap_x,mocap_y,mocap_z,mocap_q_x,\
        mocap_q_y,mocap_q_z,mocap_q_w,imu_or_x,imu_or_y,imu_or_z,imu_or_w,trajectory\n")

    tf_lis = tf_listener()
    uwb_lis = uwb_listener()
    odometry = rbot_odometry()
    imu = rbot_imu()
    mybattery = battery()
    mymocap = rbot_mocap()
    time.sleep(0.1)
    try:
        print('start')
        trajectory = 0
        trajectory_release = trajectory_timer()
        trajectory_release.start()
        while True:
            time.sleep(0.1)
            if odometry.flag:
              odom_x = odometry.turtlebot_odom_pose.pose.pose.position.x
              odom_y = odometry.turtlebot_odom_pose.pose.pose.position.y
              tf_x=tf_lis.datasub.x
              tf_y=tf_lis.datasub.y
              uwb=uwb_lis.out
              mocap_pos  = mymocap.mocapy
              odometry.flag = False
            if not mybattery.battery_is_low:
               mybattery.stop_me = False
            if (149<=mocap_pos.position.x*100<=155)and(-120<mocap_pos.position.y*100<-99) and trajectory_release.release:
              trajectory_release.releaser()
              trajectory = trajectory+1
              print(trajectory)
              if mybattery.battery_is_low:
                 mybattery.stop_me = True
                 print('stop')
            with open("All_data.csv","a") as f:
                writer = csv.writer(f,delimiter=",")
                writer.writerow([uwb[0],uwb[1],odom_x*100,odom_y*100,\
                       tf_x,tf_y,mocap_pos.position.x*100,\
                            mocap_pos.position.y*100,mocap_pos.position.z*100,mocap_pos.orientation.x,\
                                mocap_pos.orientation.y,mocap_pos.orientation.z,mocap_pos.orientation.w,\
                                     imu.turtlebot_imu.orientation.x,imu.turtlebot_imu.orientation.y,\
                                            imu.turtlebot_imu.orientation.z,\
                                                 imu.turtlebot_imu.orientation.w,trajectory])
                f.close

    except (KeyboardInterrupt, SystemExit):
        print("killed")

    print("exiting")