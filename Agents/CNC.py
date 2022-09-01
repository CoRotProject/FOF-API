# Copyright 2021 Fabrice DUVAL
import time
import threading

simulate = True
try:
    import RPi.GPIO as GPIO
    print("GPIO OK")
except ImportError:
    print("GPIO Raspberry non disponible")
    import simuraspgpio
    GPIO = simuraspgpio.GPIO_CERI()

# Status : 
# "CNC" : 
# ready : stock in/out with raw part
# busy :  stock in/out with finish part or empty
# "machine"
# full : internal stock with part
# empty : internal stock empty
# "machining" :
# running : running
# finish : not running
# "door" :
# open
# close
# "part" :
# ok
# fail (not implemented)

# CNC peut-être
# CNC_ready = 29
# machine_vide = 31
# porte_ouverte = 35
# piece_bonne = 37
# validationcobot = 11
# runprograms = [13,15] # prg1 pour 13, prg2 pour 15
# lastok = 36 #??

# CNC sur
depart_cycle = 32 # démarrage cycle sur front descendant
retour_depart_cycle = 22 # simulate
corot_mode = 31 # corot mode if one
send_corot_mode = 29 # simulate
usinage_en_cours = 33 # usinage en cours si 0
send_usinage_en_cours = 36 # simulate
etat_porte = 35 # Porte ouverte si 0
send_etat_porte = 38 # simulate

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(depart_cycle, GPIO.OUT)
GPIO.output(depart_cycle, GPIO.HIGH) # force ZERO state before start (inversed)
GPIO.setup(usinage_en_cours, GPIO.IN)
GPIO.setup(etat_porte, GPIO.IN)
GPIO.setup(corot_mode, GPIO.IN)

class CNC:
    """Fonction de commande de la machine CNC
    """
    def __init__(self, nom="Usinage_CERI"):
        self.mynom = nom
        self.liststatus = []
        self.status = {"CNC" : "ready", "machine" : "empty", "machining" : "finish", "door" : "open", "part" : "ok", }
        self.update()
        self.setready()
        

    def update(self):
        """update of CNC status"""
        if  GPIO.input(usinage_en_cours) == GPIO.HIGH: # Machining status
            self.status["machining"] = "finish"
        else:
            self.status["machining"] = "running"
        if  GPIO.input(etat_porte) == GPIO.HIGH: # Door Status
            self.status["door"] = "close"
        else:
            self.status["door"] = "open"
        if  GPIO.input(corot_mode) == GPIO.HIGH: # Machining status
            if self.status["machining"] == "running" or self.status["door"] == "close":
                self.status["CNC"] = "busy"
            else:
                self.status["CNC"] = "ready"
        else:
            self.status["CNC"] = "offline"
            
    def setready(self):
        """set machine to ready state, not fonctional"""
        return False

    def pulsestart(self):
        """1-0-1 to launch CNC cycle"""
        GPIO.output(depart_cycle, GPIO.LOW) # Low to create a '1' state
        time.sleep(0.5)
        GPIO.output(depart_cycle, GPIO.HIGH) #faling front to launch machine

    def run(self):
        """run machine drilling programme"""
        self.update()
        if self.status["CNC"] == "ready":
            # machine start
            self.pulsestart()
            print("launch machine")
            self.update()
            temps = 0
            # the door shut, and open again
            print("wait closing door")
            while self.status["door"] == "open" and not temps > 100: # and not simulate:
                self.update()
                temps += 1
                time.sleep(0.25)
            print("wait closing open")
            while self.status["door"] == "close" and not temps > 100: # and not simulate:
                self.update()
                temps += 1
                time.sleep(0.25)
            #impossible to define CNC status here (no clue of existing object)
            self.status["CNC"] = "busy"
            return self.status
        else:
            return False

    def getstatus(self):
        """return current status"""
        self.update()
        return self.status

class CNCSimulate(threading.Thread):
    """Simulation de la CNC voir debut pour connexion du raspberry
    """
    def __init__(self, name="simulateur CNC"):
        threading.Thread.__init__(self)
        self.name = name
        self.readytofalledge = False # considerate LOW level of depart_cycle
        GPIO.setup(retour_depart_cycle, GPIO.IN)
        GPIO.setup(send_usinage_en_cours, GPIO.OUT)
        GPIO.setup(send_etat_porte, GPIO.OUT)
        GPIO.setup(send_corot_mode, GPIO.OUT)
        GPIO.output(send_usinage_en_cours, GPIO.HIGH) # usinage off
        GPIO.output(send_etat_porte, GPIO.LOW) # porte ouvert
        GPIO.output(send_corot_mode, GPIO.HIGH) #corot mode
        self.running = True

    def run(self):
        loopcount = 0
        while(self.running):
            loopcount += 1
            time.sleep(0.1)
            if loopcount >= 100:
                loopcount = 0
                print("CNC simu wait for action {} {}".format("corot ON" if GPIO.input(corot_mode) == GPIO.HIGH else "corot OFF", 
                "wait for edge HIGH state" if self.readytofalledge else "wait for edge LOW"))
            if GPIO.input(corot_mode) == GPIO.LOW:
                continue
            if GPIO.input(retour_depart_cycle) == GPIO.LOW:
                self.readytofalledge = True
            if GPIO.input(retour_depart_cycle) == GPIO.HIGH:
                if self.readytofalledge == True:
                    #falling edge => run machine
                    self.readytofalledge = False
                    GPIO.output(send_etat_porte, GPIO.HIGH) #close door
                    print("CNC simu close door")
                    time.sleep(5.0)
                    GPIO.output(send_usinage_en_cours, GPIO.LOW) # usinage on
                    print("CNC simu run process")
                    time.sleep(1.0)
                    GPIO.output(send_etat_porte, GPIO.LOW) #open Door
                    print("CNC simu open door")
                    time.sleep(30.0)
                    GPIO.output(send_usinage_en_cours, GPIO.HIGH) # usinage off
                    print("CNC simu end process")

    def terminate(self):
        """clean stop"""
        print("agent simulate CNC killed")
        self.running = False

if __name__ == "__main__":
    machine = CNC()
    print(machine.getstatus())
    print("running CNC")

    if simulate:
        cncsimulate = CNCSimulate()

        cncsimulate.start()
        print("done")
        try:
            while True:
                time.sleep(10)
        except (KeyboardInterrupt, SystemExit):
            cncsimulate.terminate()
        print("killed")