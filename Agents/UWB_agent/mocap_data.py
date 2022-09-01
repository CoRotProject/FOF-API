#!/usr/bin/env python

import sys
import time
from FOF_API.MOCAP.getrigidbody import NatNetClient
body = {}
import math
 
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
     
        return roll_x, pitch_y, yaw_z # in radians


# This is a callback function that gets connected to the NatNet client
# and called once per mocap frame.

class Mocap():
    def __init__(self,clientAddress,serverAddress):
        self.clientAddress = clientAddress
        self.serverAddress = serverAddress
    def receive_new_frame(self,data_dict):
        order_list=[ "frameNumber", "markerSetCount", "unlabeledMarkersCount", "rigidBodyCount", "skeletonCount",
                    "labeledMarkerCount", "timecode", "timecodeSub", "timestamp", "isRecording", "trackedModelsChanged" ]
        dump_args = False
        if dump_args == True:
            out_string = "    "
            for key in data_dict:
                out_string += key + "="
                if key in data_dict :
                    out_string += data_dict[key] + " "
                out_string+="/"
            # print(out_string)
    # This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
    def receive_rigid_body_frame( self,new_id, position, rotation):
        # pass
        # print( "Received frame for rigid body", new_id )
        body[new_id] = [position, rotation]
        # print( "Received frame for rigid body", new_id," ",position," ",rotation )
    
    def get_body_frame(self):
        return body

    def add_lists(self,totals, totals_tmp):
        totals[0]+=totals_tmp[0]
        totals[1]+=totals_tmp[1]
        totals[2]+=totals_tmp[2]
        return totals

    def print_configuration(self,natnet_client):
        print("Connection Configuration:")
        print("  Client:          %s"% natnet_client.local_ip_address)
        print("  Server:          %s"% natnet_client.server_ip_address)
        print("  Command Port:    %d"% natnet_client.command_port)
        print("  Data Port:       %d"% natnet_client.data_port)

        if natnet_client.use_multicast:
            print("  Using Multicast")
            print("  Multicast Group: %s"% natnet_client.multicast_address)
        else:
            print("  Using Unicast")

        #NatNet Server Info
        application_name = natnet_client.get_application_name()
        nat_net_requested_version = natnet_client.get_nat_net_requested_version()
        nat_net_version_server = natnet_client.get_nat_net_version_server()
        server_version = natnet_client.get_server_version()

        print("  NatNet Server Info")
        print("    Application Name %s" %(application_name))
        print("    NatNetVersion  %d %d %d %d"% (nat_net_version_server[0], nat_net_version_server[1], nat_net_version_server[2], nat_net_version_server[3]))
        print("    ServerVersion  %d %d %d %d"% (server_version[0], server_version[1], server_version[2], server_version[3]))
        print("  NatNet Bitstream Requested")
        print("    NatNetVersion  %d %d %d %d"% (nat_net_requested_version[0], nat_net_requested_version[1],\
        nat_net_requested_version[2], nat_net_requested_version[3]))
        #print("command_socket = %s"%(str(natnet_client.command_socket)))
        #print("data_socket    = %s"%(str(natnet_client.data_socket)))

    def request_data_descriptions(self,s_client):
        # Request the model definitions
        s_client.send_request(s_client.command_socket, s_client.NAT_REQUEST_MODELDEF,    "",  (s_client.server_ip_address, s_client.command_port) )

    def my_parse_args(self,arg_list, args_dict):
        # set up base values
        arg_list_len=len(arg_list)
        if arg_list_len>1:
            args_dict["serverAddress"] = arg_list[1]
            if arg_list_len>2:
                args_dict["clientAddress"] = arg_list[2]
            if arg_list_len>3:
                if len(arg_list[3]):
                    args_dict["use_multicast"] = True
                    if arg_list[3][0].upper() == "U":
                        args_dict["use_multicast"] = False

        return args_dict


if __name__ == "__main__":

    optionsDict = {}
    optionsDict["clientAddress"] = "10.191.76.66"
    optionsDict["serverAddress"] = "10.191.76.176"
    optionsDict["use_multicast"] = False

    # This will create a new NatNet client
    #optionsDict = my_parse_args(sys.argv, optionsDict)

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

    try:
        while True:
            #time.sleep(1)
            a = euler_from_quaternion(body[13][1][0],body[13][1][1],body[13][1][2],body[13][1][3])
            print(math.degrees(a[1]))
    except (KeyboardInterrupt, SystemExit):
        streaming_client.shutdown()
    print("killed")


    print("exiting")
