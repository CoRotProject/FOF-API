import matplotlib.pyplot as plt


import matplotlib.pyplot as plt
import csv
  
x_uwb = []
y_uwb = []
x_mocap = []
y_mocap = []
x_odom = []
y_odom = []
  
with open('All_data.csv','r') as csvfile:
    lines = csv.reader(csvfile, delimiter=',')
    for row in lines:
        if (int(row[0]) < 600) and (int(row[1]) < 600):
            x_uwb.append(int(row[0]))
            y_uwb.append(int(row[1]))
            x_mocap.append(float(row[2]))
            y_mocap.append(-float(row[3]))
            x_odom.append(float(row[4])+130)
            y_odom.append(float(row[5])-100)

x_coordinates = [0, 572, 572,9]
y_coordinates = [0, 0, -394,-421]

plt.plot(x_uwb, y_uwb, color = 'g', linestyle = 'dashed',
         marker = 'o',label = "uwb")

plt.plot(x_mocap, y_mocap, color = 'b', linestyle = 'dashed',
         marker = 'o',label = "mocap")

plt.plot(x_odom, y_odom, color = 'r', linestyle = 'dashed',
         marker = 'o',label = "odom")

plt.scatter(x_coordinates, y_coordinates, label = "ancre")

  
plt.xticks(rotation = 25)
plt.xlabel('x')
plt.ylabel('y')
plt.title('trajectory', fontsize = 20)
plt.grid()
plt.legend()
plt.show()