import sys
from client_client import plc_client
sys.path.insert(0, "..")
import time
import pickle 

######## PLC client ########
#plc_man1 = plc_client(name ='plc_man1',"192.168.0.10") # no variable available in the plc opc ua for the moment
plc_man2 = plc_client(name ='plc_man2',ip="192.168.0.15")
#plciPick = plc_client(name ='plciPick',"192.168.0.20") \ no variable available in the plc opc ua for the moment
#plc_codesys = plc_client(name ='plc_codesys',"192.168.0.23")

#plc_man1.start()
plc_man2.start()
#plciPick.start()
#plc_codesys.start()


######## PLC client ########




try:
    while True:
        time.sleep(10)
except (KeyboardInterrupt, SystemExit):
    plc_man2.terminate()
print("killed")
