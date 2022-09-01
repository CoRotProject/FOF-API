import sys
sys.path.insert(0, "..")
import threading
import time
from opc_ua import opc_module
from festofactory import FestoFactory

class palette(threading.Thread):
    def __init__(self,numero_palette):
        threading.Thread.__init__(self)
        self.nbr_palette = numero_palette
        self.property = {'nbr':self.nbr_palette,"station":"station","station_dis":0,"passed_sensor":"passed_sensor","load":0}
        #self.location_palette()
        print(self.property)
        mutex_semaphore = threading.Lock()
        self.running = True

    def location_palette(self):
        if self.rfid_sensor == "man2NumeroPalette1":
            self.property["station"]= "man2"
            self.property["station_dis"]= "40"
        if self.rfid_sensor == "man2NumeroPalette2":
            self.property["station"]= "man2"
            self.property["station_dis"]= "60"

    def run(self):
        while self.running:
            pass
                
    def terminate(self):
         """clean stop"""
         self.running = False
         self.plc_man2.terminate()

            

if __name__ == "__main__":
    plc_man2 = opc_module(name ='plc_man2',addresse="10.191.76.20:4841")
    plc_man2.start()
    time.sleep(2)
    print(plc_man2.get_data())


    mapallete = palette(5,"man2NumeroPalette2")
    mapallete.start()
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        mapallete.terminate()
    print("killed")