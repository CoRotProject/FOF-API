import sys
import time
import settings
from FOF_API.Agents.UWB_agent.odometry_data import rbot_odometry
from FOF_API.Agents.UWB_agent.uwb_data1 import uwb_data
from FOF_API.Agents.UWB_agent.tf_listener import tf_listener
from FOF_API.Agents.UWB_agent.mocap_data import Mocap
from FOF_API.MOCAP.getrigidbody import NatNetClient
import csv

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

    data_file = open('All_data.csv', 'w+')
    data_file.write("x_uwb,y_uwb,x_odom,y_odom,tf_x,tf_y,mocap_x,mocap_y\n")
    uwb_get_way = uwb_data('IDRdata.csv',"/dev/ttyACM2")
    uwb_get_way.start()
    tf_lis = tf_listener()
    ex = rbot_odometry()
    time.sleep(0.1)
    try:
        print('start')
        while True:
            uwb_val = settings.myList
            #print(uwb_val)
            time.sleep(0.1)
            if ex.flag:
              odom_x = ex.turtlebot_odom_pose.pose.pose.position.x
              odom_y = ex.turtlebot_odom_pose.pose.pose.position.y
              tf_x=tf_lis.datasub.x
              tf_y=tf_lis.datasub.y
              ex.flag = False
            if uwb_val!=[]:
              with open("All_data.csv","a") as f:
                 writer = csv.writer(f,delimiter=",")
                 writer.writerow([uwb_val[0],uwb_val[1],odom_x*100,odom_y*100,tf_x,tf_y,mymocap.get_body_frame()[13][0][0]*100,mymocap.get_body_frame()[13][0][2]*100])
                 f.close

    except (KeyboardInterrupt, SystemExit):
        print("killed")

    print("exiting")

