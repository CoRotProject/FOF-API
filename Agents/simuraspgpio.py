# Copyright 2021 Fabrice DUVAL
# import RPi.GPIO as GPIO

# CNC sur
depart_cycle = 32 # démarrage cycle sur front descendant
retour_depart_cycle = 22 # simulate
corot_mode = 31 # corot mode if one
send_corot_mode = 29 # simulate
usinage_en_cours = 33 # usinage en cours si 0
send_usinage_en_cours = 36 # simulate
etat_porte = 35 # Porte ouverte si 0
send_etat_porte = 38 # simulate


class GPIO:
    """simulateur de port GPIO"""
    def __init__(self):
        self.BOARD = "board"
        self.OUT = "out"
        self.IN = "in"
        self.etats = [True for a in range(64)]
        self.HIGH = True
        self.LOW = False

    def setmode(self, mode):
        print("setmode " + mode)

    def setwarnings(self, valeur):
        print("setwarning")
        print(valeur)

    def setup(self, port, etat):
        print("setup " + str(port) + "==>" + etat)

    def input(self, num):
        # GPIO.input (33)
        # self.etats[num] = not self.etats[num]
        if self.etats[num]:
            return self.HIGH
        else:
            return self.LOW

    def output(self, port, etat):
        # GPIO.output(portout, GPIO.LOW)
        self.etats[port] = (etat == self.HIGH)
        print("output " + str(port) + "==>" + ("HIGH" if etat else "LOW"))

# CNC sur
depart_cycle = 32 # démarrage cycle sur front descendant
retour_depart_cycle = 22 # simulate
corot_mode = 31 # corot mode if one
send_corot_mode = 29 # simulate
usinage_en_cours = 33 # usinage en cours si 0
send_usinage_en_cours = 36 # simulate
etat_porte = 35 # Porte ouverte si 0
send_etat_porte = 38 # simulate

class GPIO_CERI(GPIO):
    def output(self, port, etat):
        # print("porte {} ".format(self.etats[etat_porte]))
        # print("usinage {} ".format(self.etats[usinage_en_cours]))
        # GPIO.output(portout, GPIO.LOW)
        port2 = 999
        self.etats[port] = (etat == self.HIGH)
        if port == send_corot_mode:
            port2 = corot_mode
        elif port == send_usinage_en_cours:
            port2 = usinage_en_cours
        elif port == send_etat_porte:
            port2 = etat_porte
        elif port == depart_cycle:
            port2 = retour_depart_cycle

        print("output " + str(port) + "==>" + ("HIGH" if etat else "LOW"))
        if not port2 == 999:
            print("lien " + str(port2) + "==>" + ("HIGH" if etat else "LOW"))
            self.etats[port2] = self.etats[port]