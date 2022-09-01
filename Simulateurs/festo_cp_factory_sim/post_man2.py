import pandas as pd
import time



class post_man2():
    def __init__(self,palette,opcua_var,lpp_palette):
        self.palette=palette
        self.opcua_var=opcua_var
        self.dis_belt1= 1.154 # in metre
        self.dis_belt2 = self.dis_belt1
        self.pose_sensor_change_2= 0.025
        self.conveyor_speed = 0.12 #m/s
        self.pose_RFID1 = 0.775
        self.pose_RFID2 = 0.20
        self.lpp_palette = lpp_palette
        
    def find_val_sensor(self,sensor):
        index=self.opcua_var['var_name'].index(sensor)
        return self.opcua_var['value'][index]
    
    def find_palette(self,sensor):
        index = self.palette['last_past_post_id'].index(sensor)

    def tempo(self,sleeptime):
        time.sleep(sleeptime)
        return True
    
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
        elif wait_f_sensor=='presence_RFID2':
            added_distance = 0
            parrapport = 'conv 2'
        while time.time() < mustend:
            distance = (self.conveyor_speed*(time.time()-start)+ added_distance)/(self.dis_belt1)*100
            if distance < 100:
                print('distance parcourue // '+parrapport+': ',distance,'%')
            if condition: 
                print('une palette est arrivée au capteur',wait_f_sensor)
                return True
            time.sleep(period)
        print('une palette n\'est pas arrivé à temps au capteur',wait_f_sensor)
        return False


    def run(self):
        int_sensor=self.find_val_sensor('in_sensor')
        if int_sensor == True:
            timeout1 = (self.pose_RFID1/self.conveyor_speed)*1.1
            self.wait_until('presence_RFID1',timeout1)
            palette_id = self.find_val_sensor('RFID1') 
            print('la palette détecté est le numero ',palette_id)
            if palette_id == self.lpp_palette:
                print ('la palette',self.lpp_palette,'a bien arrivé')
            else:
                print ('la palette',self.lpp_palette,'a disparu')

            timeout2 = (self.dis_belt1-self.pose_RFID1)/self.conveyor_speed*1.2
            self.wait_until('conv_change_1',timeout2)

            timeout3 = (self.pose_sensor_change_2)/self.conveyor_speed*1.1
            self.wait_until('conv_change_2',timeout3)

            timeout4 = (self.pose_RFID2)/self.conveyor_speed*1.1
            self.wait_until('presence_RFID2',timeout4)

            timeout4 = (self.pose_RFID2)/self.conveyor_speed*1.1
            self.wait_until('out_sensor',timeout4)
   

palette = {'id':[1,2,3,4,5,6,7,8,9,10,11,12,13,14],
        'current_post':['man2', 'man1', 'four', 'drill','magasin','robot','man2', 'drill', 'four', 'drill','magasin','robot',\
            'man2', 'man2'],
        'pos_in_post':[10,25,2,80,5,6,7,8,9,10,11,12,13,14],
        'pos_in_factory':[10,25,2,80,5,6,7,8,9,10,11,12,13,14],
        'defaut':[0,1,0,1,1,1,0,0,1,0,1,0,1,0],
        }
lpp_palette = 10


opcua_var = {'var_name':['presence_RFID1','RFID1','presence_RFID2', 'RFID2', 'stop_button', 'stopper1','stopper2','routing','conv1','conv2','conv_change_1','conv_change_2','Prox_sensors','out_sensor','in_sensor'\
            ,'dev_in_sensor','dev_ou_sensor','dev_conv1','dev_conv2','dev_stop'],
        'label':['presence_RFID1','RFID1','presence_RFID2', 'RFID2', 'stop_button', 'stopper1','stopper2','routing','conv1','conv2','conv_change_1','conv_change_2','Prox_sensors','out_sensor','in_sensor'\
            ,'dev_in_sensor','dev_ou_sensor','dev_conv1','dev_conv2','dev_stop'],
        'value':[False,10]+[None]*12+[True]+[None]*5,
        #'type':['int','bool','real','class'],
        #'source':['int','bool','real','class'],
        'description':['presence_RFID1','RFID1','presence_RFID2', 'RFID2', 'stop_button', 'stopper1','stopper2','routing','conv1','conv2','conv_change_1','conv_change_2','Prox_sensors','out_sensor','in_sensor'\
            ,'dev_in_sensor','dev_ou_sensor','dev_conv1','dev_conv2','dev_stop']
        }


# Create DataFrame
palette_Ttable = pd.DataFrame(palette)
OPC_UA_VAR_Table = pd.DataFrame(opcua_var)
print(palette_Ttable,'\n')
print(OPC_UA_VAR_Table,'\n')

post_man_2 = post_man2(palette,opcua_var,lpp_palette)
post_man_2.run()