import pandas as pd

print("plc_man2")
plc_man2 = {'var_name':['RFID1', 'RFID2', 'stop_button', 'stopper1','stopper2','routing','conv1','conv2','conv_change_1','conv_change_2','Prox_sensors','out_sensor','in_sensor'\
            ,'dev_in_sensor','dev_ou_sensor','dev_conv1','dev_conv2','dev_stop'],
        'label':['RFID1', 'RFID2', 'stop_button', 'stopper1','stopper2','routing','conv1','conv2','conv_change_1','conv_change_2','Prox_sensors','out_sensor','in_sensor'\
            ,'dev_in_sensor','dev_ou_sensor','dev_conv1','dev_conv2','dev_stop'],
        'value':[None] * 18,
        #'type':['int','bool','real','class'],
        #'source':['int','bool','real','class'],
        'description':['RFID1', 'RFID2', 'stop_button', 'stopper1','stopper2','routing','conv1','conv2','conv_change_1','conv_change_2','Prox_sensors','out_sensor','in_sensor'\
            ,'dev_in_sensor','dev_ou_sensor','dev_conv1','dev_conv2','dev_stop']
        }
# Create DataFrame
df = pd.DataFrame(plc_man2)
print(df,'\n')

