import serial
import serial
from time import sleep
import threading
import time
# sudo chmod 666 /dev/ttyACM0
device_port = "/dev/ttyACM0"
from multiprocessing.pool import ThreadPool
import settings

class uwb_data(threading.Thread):
    def __init__(self,file_name,device_port):
        threading.Thread.__init__(self)
        self.file_name = file_name
        self.serial = serial.Serial(device_port)
        self.running = True
        self.myval = []

    def create_csv_file(self):
        self.f = open(self.file_name, 'w+')
        self.f.write("timestamp,x,y,z \n")
        sleep(1)

    def store_uwb_data(self):
        val = str(self.serial.readline().decode().strip(' \r\n'))
        if val.startswith('+DPOS:'):
            val = val.strip('+DPOS:')
            val = val.split(',')
            self.myval =  [int(float(val[2])),int(float(val[3]))]
    
    def get_uwb_data(self):
        return self.myval
    
    
    def run(self):
        while self.running:
            self.store_uwb_data()
            settings.myList = self.get_uwb_data()

    def terminate(self):
         """clean stop"""
         self.running = False




if __name__ == "__main__":
    uwb_get_way = uwb_data('IDRdata.csv',"/dev/ttyACM0")
    uwb_get_way.start()
    pool = ThreadPool(processes=1)
    try:
        while True:
            async_result = pool.apply_async(uwb_get_way.get_uwb_data) 
            return_val = async_result.get()
            print(settings.myList)

    except (KeyboardInterrupt, SystemExit):
        uwb_get_way.terminate()
    print("killed")