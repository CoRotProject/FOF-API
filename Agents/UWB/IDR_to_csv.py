import serial
from time import sleep
from time import time, strftime, localtime
import sys

COM4 = 'spy://COM8'
BAUD = 115200

ser = serial.serial_for_url(COM4, baudrate=BAUD, timeout=5)



file_name = 'IDRdata.csv'
print('Waiting for device');
f = open(file_name, 'w+')
f.write("timestamp,x,y,z,localtime,\n")
sleep(1)

print(ser.name)

#check args
if("-m" in sys.argv or "--monitor" in sys.argv):
	monitor = True
else:
	monitor= False

while True:
	val = str(ser.readline().decode().strip(' \r\n'))#Capture serial output as a decoded string
	#if val.startswith('+DPOS:'):
		#space=val.index(" ")
	f.write(val+strftime("%H:%M:%S,", localtime())+"\n")

f.close()