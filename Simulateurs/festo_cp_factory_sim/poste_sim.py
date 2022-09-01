import json
import time
import test

class poste_sim:
    def __init__(self,poste_name):
         self.poste_name = poste_name
         self.poste_json = self.poste_name+'.json'
         self.json = open(self.poste_json)
         self.data = json.load(self.json )
         parent =self.data[poste_name]
         self.poste_items={}
         self.get_child(parent)
         print(self.poste_items)
         self.running = True


    def get_child(self,parent):
        for i in range(len(parent)):
            self.poste_items[parent[i]['name']] = []
            for j in range(len(parent[i]['child'])):
                self.poste_items[parent[i]['name']].append(parent[i]['child'][j]['name'])
                self.poste_items[parent[i]['name']].append(parent[i]['child'][j]['distance'])
            self.get_child(parent[i]['child'])
    
    def find_val_sensor(self,sensor):
        index=self.opcua['name'].index(sensor)
        return self.opcua['Rising_front'][index]
    
    def wait_until(self,wait_f_sensor, timeout, period=0.25):

        start = time.time()
        mustend = start + timeout
        condition = self.find_val_sensor(wait_f_sensor)
        if wait_f_sensor == 'presence_RFID1':
            added_distance = 0
            parrapport = 'conv 1'
        elif wait_f_sensor == 'conv_change_1':
            added_distance = self.pose_RFID1
            parrapport = 'conv 1'
        elif wait_f_sensor=='conv_change_2':
            added_distance = 0
            parrapport = 'conv 2'
        while time.time() < mustend:
            distance = (self.conveyor_speed*(time.time()-start)+ added_distance)/(self.dis_belt1+self.demi_courbure)*100
            if distance < 100:
                print('distance parcourue // '+parrapport+': ',distance,'%')
            if condition: 
                return True
            time.sleep(period)
        return False

    def run(self):
        while self.running:
        return

    def terminate(self):
         """clean stop"""
         self.running = False

            

poste_man2= poste_sim('poste_man2')

poste_man2.run()
try:
    while True:
        time.sleep(10)
except (KeyboardInterrupt, SystemExit):
    poste_man2.terminate()
print("killed")
