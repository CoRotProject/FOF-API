import matplotlib.pyplot as plt
import csv
import math  
EQUAL_THRESHOLD=1e-3

x_uwb = []
y_uwb = []
x_amcl = []
y_amcl = []
x_odom = []
y_odom = []
x_mocap = []
y_mocap = []
x_mocap_n = []
y_mocap_n = []
x_mocap_q = []
y_mocap_q = []
z_mocap_q = []
w_mocap_q = []
orientation = []
orientation_x = []
orientation_y = []
orientation_z = []
orientation_new = []
angle = []
mbr = []
x_uwb_n = []
y_uwb_n =[]

def euler_from_quaternion(x, y, z, w):
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)
        return roll_x, pitch_y, yaw_z # in radians
i = 0
passed = 0
with open('All_data.csv','r') as csvfile:
    lines = csv.reader(csvfile, delimiter=',')
    for row in lines:
        if ((-800< int(row[0]) < 600) and (-400< int(row[1]) < 300)) and float(row[-1])!=16 and float(row[-1])!=29:
            if -300 >float(row[7]):
                if passed == float(row[-1]):
                    pass
                else:
                    print(row[-1])
                passed = float(row[-1])
            x_uwb.append(int(row[0])-25)
            y_uwb.append(int(row[1])+70)
            x_amcl.append(float(row[4])+167)
            y_amcl.append(float(row[5])-100)
            x_odom.append(float(row[2]))
            y_odom.append(float(row[3]))
            x_mocap.append(float(row[6]))
            y_mocap.append(float(row[7]))
            x_mocap_q.append(float(row[9]))
            y_mocap_q.append(float(row[10]))
            z_mocap_q.append(float(row[11]))
            w_mocap_q.append(float(row[12]))
            angle.append(euler_from_quaternion(x_mocap_q[-1],y_mocap_q[-1],z_mocap_q[-1],w_mocap_q[-1])[2])
            orientation.append(math.degrees(angle[-1]))
            x_mocap_n.append(x_mocap[-1]-13.4*math.cos(angle[-1])-9.25*math.sin(angle[-1]))
            y_mocap_n.append(y_mocap[-1]-13.4*math.sin(angle[-1])+9.25*math.cos(angle[-1]))
            x_uwb_n.append(x_uwb[-1]+21.2*math.cos(angle[-1]))
            y_uwb_n.append(y_uwb[-1]+21.2*math.sin(angle[-1]))
            mbr.append(i)
            i= i+1

x_coordinates = [0, 690.012+16.05, 629.654+16.05,-17.068+16.05]
y_coordinates = [0, -67.89+25.84, -569.792+25.684,-474.266+5.684]

plt.plot(x_uwb, y_uwb, color = 'g', linestyle = 'dashed',
         marker = 'o',label = "uwb")
plt.plot(x_uwb_n, y_uwb_n, color = 'y', linestyle = 'dashed',
         marker = 'o',label = "uwb_n")

plt.plot(x_amcl, y_amcl, color = 'b', linestyle = 'dashed',
         marker = 'o',label = "amcl")

'''plt.plot(x_odom, y_odom, color = 'r', linestyle = 'dashed',
         marker = 'o',label = "odom")'''

'''plt.plot(x_mocap, y_mocap, color = 'm', linestyle = 'dashed',
         marker = 'o',label = "x_mocap")'''

plt.plot(x_mocap_n, y_mocap_n, color = 'm', linestyle = 'dashed',
         marker = 'o',label = "y_mocap_n")
'''plt.plot(mbr, orientation, color = 'g', linestyle = 'dashed',
         marker = 'o',label = "orientation_new")'''

plt.scatter(x_coordinates, y_coordinates, label = "ancre")


#print(orientation_new[1:50])
  
plt.xticks(rotation = 25)
plt.xlabel('x')
plt.ylabel('y')
plt.title('2D position of a robot using different localization systems', fontsize = 20)
plt.grid()
plt.legend()
plt.show()
