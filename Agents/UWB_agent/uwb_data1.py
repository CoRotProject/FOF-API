import serial
import serial
from time import sleep
import threading
import time
# sudo chmod 666 /dev/ttyACM0
import settings
import csv
device_port = "/dev/ttyACM1"

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
        val = str(self.serial.readline().decode('ascii').strip(' \r\n'))
        if val.startswith('+MPOS:'):
            val = val.strip('+MPOS:')
            val = val.split(',')
            if len(val)==6:
               try:
                  self.myval =  [int(float(val[1])),int(float(val[2]))]
               except IndexError:
                  pass
    def get_uwb_data(self):
        return self.myval
    def run(self):
        while self.running:
            self.store_uwb_data()
            settings.myList = self.get_uwb_data()
            print(settings.myList)
            if self.get_uwb_data()!=[]:
              with open("IDRdata.csv","a") as f:
                writer = csv.writer(f,delimiter=",")
                writer.writerow([self.get_uwb_data()[0],self.get_uwb_data()[1]])
                #"self.f.write(str(self.get_uwb_data()[0])+","+str(self.get_uwb_data()[1])+'\n')
                f.close

    def terminate(self):
         """clean stop"""
         self.running = False
         




if __name__ == "__main__":
    uwb_get_way = uwb_data('IDRdata.csv',"/dev/ttyACM1")
    uwb_get_way.create_csv_file()
    uwb_get_way.start()
    try:
        sleep(0.1)
        #print(settings.myList)
    except (KeyboardInterrupt, SystemExit):
        uwb_get_way.terminate()
#print("killed")
