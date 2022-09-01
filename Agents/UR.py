# coding: utf8
# Echo client program
import socket
import time
import struct
import re
import quaternionTransforms

#par défaut UR10
HOST = "10.191.76.119"
PORT0 = 29999
PORT1 = 30001
PORT2 = 30002
PORT3 = 30003

class arm:
    def __init__(self, host = HOST):
        self.HOST = host # The remote host
        self.PORT0 = PORT0
        self.PORT1 = PORT1
        self.PORT2 = PORT2
        self.PORT3 = PORT3
        self.restart()
    
    def reset(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((self.HOST, self.PORT0))
        firsttxt = s.recv(128)
        if len(firsttxt) < 10:
            return False

        def sendquestion(txt):
            if isinstance(txt,str):
                txt = txt.encode('ascii', 'replace')
            s.send(txt + b"\n")
            return s.recv(128)

        def getanswer(txt):
            retour = sendquestion(txt)
            return retour[retour.find(b':')+2:-1].upper()
        
        sendquestion(b"power off")
        loop = 0
        time.sleep(1)
        while getanswer(b"robotmode") != b"POWER_OFF":
            loop += 1
            if loop >= 10:
                s.close()
                return "TO POWER_OFF FAIL"
            time.sleep(1)
        s.close()
        return self.restart()
  
    def restart(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((self.HOST, self.PORT0))
        firsttxt = s.recv(128)
        if len(firsttxt) < 10:
            return False

        def sendquestion(txt):
            if isinstance(txt,str):
                txt = txt.encode('ascii', 'replace')
            s.send(txt + b"\n")
            return s.recv(128)

        def getanswer(txt):
            retour = sendquestion(txt)
            return retour[retour.find(b':')+2:-1].upper()
        
        if getanswer(b"robotmode") == b"POWER_OFF":
            sendquestion(b"power on")
            loop = 0
            time.sleep(1)
            while getanswer(b"robotmode") != b"IDLE":
                loop += 1
                if loop >= 10:
                    s.close()
                    return "FROM POWER_OFF FAIL"
                time.sleep(1)
            sendquestion(b"brake release")
            time.sleep(1)
            loop = 0
            while getanswer(b"robotmode") != b"RUNNING":
                loop += 1
                if loop >= 10:
                    s.close()
                    return "FROM IDLE FAIL"
                time.sleep(1)
            return "FROM POWER_OFF OK"
        elif getanswer(b"safetymode") == b"PROTECTIVE_STOP":
            sendquestion(b"unlock protective stop")
            time.sleep(1)
            loop = 0
            while getanswer(b"safetymode") != b"NORMAL":
                loop += 1
                if loop >= 10:
                    s.close()
                    return "FROM PROTECTIVE STOP FAIL"
        s.close()
        return "Nothing solvable"

    def sendcommand(self, nom, position=None, **parametres):
        if position:
            if len(position) == 7: #angle quaternion
                postrigo = position[:3]
                angle = quaternionTransforms.quaternion_to_angle_axis(position[3:7], fusion=True)
            elif len(position) == 6: #angle-axis
                postrigo = position[:3]
                angle = position[3:6]
            elif isinstance(position, dict): #from database
                postrigo = [position["position"]["x"], position["position"]["y"], position["position"]["z"]]
                angle = quaternionTransforms.quaternion_to_angle_axis(position["rotation"], fusion=True)
            parametres["posx"], parametres["posy"], parametres["posz"] = postrigo[0], postrigo[1], postrigo[2]
            parametres["posrx"], parametres["posry"], parametres["posrz"] = angle[0], angle[1], angle[2]

        data = self.convertdata(nom, **parametres)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((self.HOST, self.PORT2))
        s.send (data.encode('ascii', 'replace'))
        # data = s.recv(1024)
        s.close()
        print("Commande envoyee")

    def convertdata(self, nom, **parametres):
        with open(nom, 'r') as file: # Use file to refer to the file object
            data = file.read()
        print("Execution du Scritp", nom)
        if len(data) > 0:
            # data = data.encode('ascii','replace')
            for variable in parametres:
                print('parametre', variable, 'modifie (ou cree) en', parametres[variable])
                position = re.search(r'.*' + variable + r'\s*=.*', data, re.MULTILINE)
                print(position)
                if position != None:
                    data= data[:position.regs[0][0]] + re.sub(r"(.*)=(.*)", r"\1=" + str(parametres[variable]), data[position.regs[0][0]:position.regs[0][1]]) + data[position.regs[0][1]:]
                else:
                    position = re.search(r'.*def .*\n', data, re.MULTILINE)
                    if position != None:
                        data = data[:position.regs[0][1]] + "  global " + variable + " = " + str(parametres[variable]) + r'\n' + data[position.regs[0][1]:]
        return data

    def extractdoublearray(self, tab_bytes, offset, taille):
        return [struct.unpack('>d', tab_bytes[i*8+offset:i*8 + offset + 8])[0] for i in range(taille)]

    def lire_statut(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((self.HOST, self.PORT3))
        data = s.recv(1108)
        Parametres = {}
        Parametres["Size"] = int.from_bytes(data[0:4], 'big')
        Parametres["Time"] = self.extractdoublearray(data, 4, 1)
        Parametres["q_target"] = self.extractdoublearray(data, 12, 6)
        Parametres["qd_target"] = self.extractdoublearray(data, 60, 6)
        Parametres["qdd_target"] = self.extractdoublearray(data, 108, 6)
        Parametres["I_target"] = self.extractdoublearray(data, 156, 6)
        Parametres["M_target"] = self.extractdoublearray(data, 204, 6)
        Parametres["q_actual"] = self.extractdoublearray(data, 252, 6)
        Parametres["qd_actual"] = self.extractdoublearray(data, 300, 6)
        Parametres["I_actual"] = self.extractdoublearray(data, 348, 6)
        Parametres["I_control"] = self.extractdoublearray(data, 396, 6)
        Parametres["Tool_vector_actual"] = self.extractdoublearray(data, 444, 6)
        Parametres["TCP_speed_actual"] = self.extractdoublearray(data, 492, 6)
        Parametres["TCP_force"] = self.extractdoublearray(data, 540, 6)
        Parametres["Tool_vector_target"] = self.extractdoublearray(data, 588, 6)
        Parametres["TCP_speed_target"] = self.extractdoublearray(data, 636, 6)
        Parametres["Digital_input_bits"] = self.extractdoublearray(data, 684, 1)
        Parametres["Motor_temperatures"] = self.extractdoublearray(data, 692, 6)
        Parametres["Controller_Timer"] = self.extractdoublearray(data, 740, 1)
        Parametres["Test_value"] = self.extractdoublearray(data, 748, 1)
        Parametres["Robot_Mode"] = self.extractdoublearray(data, 756, 1)
        Parametres["Joint_Modes"] = self.extractdoublearray(data, 764, 6)
        Parametres["Safety_Mode"] = self.extractdoublearray(data, 812, 1)
        Parametres["Internal_1"] = self.extractdoublearray(data, 820, 6)
        Parametres["Tool_Accelerometer_values"] = self.extractdoublearray(data, 868, 3)
        Parametres["Internal_2"] = self.extractdoublearray(data, 892, 6)
        Parametres["Speed_scaling"] = self.extractdoublearray(data, 940, 1)
        Parametres["Linear_momentum_norm"] = self.extractdoublearray(data, 948, 1)
        Parametres["Internal_3"] = self.extractdoublearray(data, 956, 1)
        Parametres["Internal_4"] = self.extractdoublearray(data, 964, 1)
        Parametres["V_main"] = self.extractdoublearray(data, 972, 1)
        Parametres["V_robot"] = self.extractdoublearray(data, 980, 1)
        Parametres["I_robot"] = self.extractdoublearray(data, 988, 1)
        Parametres["V_actual"] = self.extractdoublearray(data, 996, 6)
        Parametres["Digital_outputs"] = self.extractdoublearray(data, 1044, 1)
        Parametres["Program_state"] = self.extractdoublearray(data, 1052, 1)
        Parametres["Elbow_position"] = self.extractdoublearray(data, 1060, 3)
        Parametres["Elbow_velocity"] = self.extractdoublearray(data, 1084, 3)
        s.close()
        return Parametres

    def wait_endmove(self, temps_contrainte=1.0, vitesseforunmove=0.1, timeout = 10.0):
        vitesse = 10000
        time_start = time.time()

        vitesses = self.lire_statut()["qd_actual"]
        vitesses = [abs(vit) for vit in vitesses]
        vitesse = max(vitesses)
        while vitesse < vitesseforunmove:
            # not started yet
            time.sleep(0.25)
            vitesses = self.lire_statut()["qd_actual"]
            vitesses = [abs(vit) for vit in vitesses]
            vitesse = max(vitesses)
            if time.time() > time_start + timeout:
                return time_start - time.time() # Error (<0)

        time_start_pause = time.time()
        while time.time() < time_start_pause + temps_contrainte:
            vitesses = self.lire_statut()["qd_actual"]
            vitesses = [abs(vit) for vit in vitesses]
            vitesse = max(vitesses)
            while vitesse > vitesseforunmove:
                vitesses = self.lire_statut()["qd_actual"]
                vitesses = [abs(vit) for vit in vitesses]
                vitesse = max(vitesses)
                time.sleep(0.1)
                time_start_pause = time.time() # Il bouge donc pas en pause
        return time.time() - time_start

    def wait_endprog(self, timeout = 5.0, timemax = 15.0):
        temps0 = time.time()
        while self.lire_statut()["Program_state"][0] != 2.0:
            time.sleep(0.25)
            if time.time() >= timeout + temps0:
                return temps0 - time.time() # Error (<0)

        while self.lire_statut()["Program_state"][0] != 1.0:
            time.sleep(0.25)
            if time.time() >= temps0 + timemax:
                return time.time() - temps0
        return time.time() - temps0


if __name__ == "__main__":
    print("Commandes UR")
    print("En cours : " + HOST + ":" + str(PORT2))
    print("exemple")
    print("""
    robot = UR("10.191.76.119",30002)
    robot.sendcommand("stock2imprimante.script",Selected_Boite = 5)
    """)

    robot = arm(HOST)
    # robot.reset()
    robot.sendcommand("ur10_t/grab.ascript", delta_saisie=0.10)
    print("Waiting...")
    # print(robot.wait_endprog(timemax = 1.0))
    # print(robot.wait_endmove())
    # robot.sendcommand("ur10_t/grab.ascript", delta_saisie=0.10, posx=-0.1)
    # print(robot.wait_endprog())
    # robot.sendcommand("ur10_t/grab.ascript", position=[0.0, 0.6, 0.3, 0, 3.14, 0], delta_saisie=0.10)
    # print(robot.wait_endmove())
    robot.sendcommand("ur10_t/grab.ascript", position=[0.0, 0.9, 0.2, 0, 1, 0, 0], delta_saisie=0.10)
    print(robot.wait_endmove())
    print("Program finish")
