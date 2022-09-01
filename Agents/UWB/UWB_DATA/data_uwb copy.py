
import operator
import serial
import requests
import serial
from time import sleep
from time import time, strftime, localtime
import sys
import csv


# sudo chmod 666 /dev/ttyACM0
device_port = "/dev/ttyACM0"
#serial = serial.Serial(device_port)


class uwb_data():
    def __init__(self,file_name,device_port):
        self.file_name = file_name
        self.serial = serial.Serial(device_port)

    def create_csv_file(self):
        self.f = open(self.file_name, 'w+')
        #self.f.write("x,y \n")
        sleep(1)
    def store_uwb_data(self):
        try:
            while True:
                val = str(self.serial.readline().decode().strip(' \r\n'))
                if val.startswith('+DPOS:'):
                    val = val.strip('+DPOS:')
                    val = val.split(',')
                    #val = val[2]
                    return int(val[2])
                    self.f.write(val[2]+','+val[3]+"\n")
        except KeyboardInterrupt:
            pass

uwb_get_way = uwb_data('IDRdata.csv',"/dev/ttyACM0")
uwb_get_way.create_csv_file()
uwb_get_way.store_uwb_data()