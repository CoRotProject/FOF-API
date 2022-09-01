from time import sleep
from FOF_API.Agents.mir_api.mir_utils import mymir
import operator

import serial
import requests

# sudo chmod 666 /dev/ttyACM0
device_port = "/dev/ttyACM1"
serial = serial.Serial(device_port)



try:
    while True:
        sleep(0.8)
        line = str(serial.readline())
        fb = line
        #if fb.startswith('b\'+DIMU:'):
        print(line)
        '''fb_cmd = fb[0:5]
        fb_data = fb[6:-1].replace("\r\n","").split(",")
        time = fb_data[0]
        robot_id = fb_data[1]'''
        #if fb_cmd == "+DPOS" and (robot_id == "4D144137" or robot_id == "D141C33" or robot_id == "D02D092" or robot_id == "4D025C9F"):
        #    print(fb_data[2:5])
except KeyboardInterrupt:
    pass
