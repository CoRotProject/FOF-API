import sys
sys.path.insert(0, "..")
from opcua import Client 
import threading
import time
import json
import os
from opc_ua import opc_module


class pallete(threading.Thread):
    def __init__(self,file,):
        threading.Thread.__init__(self)
        self.file = file
        self.running = True
        self.plc_man2 = opc_module(name ='plc_man2',addresse="10.191.76.20:4841")
        self.plc_man2.start()
        self.plc_man1 = opc_module(name ='plc_man1',addresse="10.191.76.20:4840")
        self.plc_man1.start()
        self.plc_ipick = opc_module(name ='ipick',addresse="10.191.76.20:4842")
        self.plc_ipick.start()
        time.sleep(2)
        print('connection set properly')
        self.pasterfid = self.get_rfid()

    def get_rfid(self):
        rfid_dic= {}
        try:
            rfid_dic ['man2NumeroPalette1'] = self.plc_man2.get_data()['man2NumeroPalette1'][0]
            rfid_dic ['man2NumeroPalette2'] = self.plc_man2.get_data()['man2NumeroPalette2'][0]
            rfid_dic ['man1NumeroPalette1'] = self.plc_man1.get_data()['man1NumeroPalette1'][0]
            rfid_dic ['man1NumeroPalette2'] = self.plc_man1.get_data()['man1NumeroPalette2'][0]
            rfid_dic ['IpickNumeroPalette1'] = self.plc_ipick.get_data()['IpickNumeroPalette1'][0]
            rfid_dic ['IpickNumeroPalette2'] = self.plc_ipick.get_data()['IpickNumeroPalette2'][0]
            rfid_dic ['ASR32NumeroPaletteG'] = self.plc_man2.get_data()['ASR32NumeroPaletteG'][0]
            rfid_dic ['ASR32NumeroPaletteD'] = self.plc_man2.get_data()['ASR32NumeroPaletteD'][0]
            rfid_dic ['PressNumeroPalette'] = self.plc_man2.get_data()['PressNumeroPalette'][0]
            rfid_dic ['DrillNumeroPalette'] = self.plc_man2.get_data()['DrillNumeroPalette'][0]
            rfid_dic ['HeatingNumeroPalette'] = self.plc_man2.get_data()['HeatingNumeroPalette'][0]
            rfid_dic ['HeatingNumeroPalette'] = self.plc_man2.get_data()['HeatingNumeroPalette'][0]
            rfid_dic ['MagIONumeroPalette'] = self.plc_man2.get_data()['MagIONumeroPalette'][0]
            rfid_dic ['RASSNumeroPaletteD'] = self.plc_man2.get_data()['RASSNumeroPaletteD'][0]
            rfid_dic ['RASSNumeroPaletteG'] = self.plc_man2.get_data()['RASSNumeroPaletteG'][0]
        except:
            print("exeption")
            pass
        if rfid_dic != {}:
            return rfid_dic
        else:
            return self.pasterfid

    def run(self):
        while self.running:
            if (self.pasterfid["man2NumeroPalette2"] != self.get_rfid()["man2NumeroPalette2"]) or (self.pasterfid["man2NumeroPalette1"] != self.get_rfid()["man2NumeroPalette1"]):
                print(self.get_rfid())
                self.pasterfid = self.get_rfid()
                
    
    def terminate(self):
         """clean stop"""
         self.running = False
         self.plc_man2.terminate()

            

if __name__ == "__main__":

    mapallete = pallete(file ='plc_man2')
    mapallete.start()
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        mapallete.terminate()
    print("killed")
