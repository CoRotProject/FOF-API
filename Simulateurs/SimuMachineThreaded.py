# coding: utf8
# Copyright 2020 Fabrice DUVAL
from __future__ import print_function
# import requests
import sys
# import pymongo
import time
import threading
import math
import sys
# sys.path.append("..\\Commandes")
import Commandes.commandeAPI as commandeAPI
#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

position = {
    "poste1":{"x":36.25, "y":2.09, "theta":138.4, },
    "poste2":{"x":33.38, "y":-2.65, "theta":135.1, },
    "poste3":{"x":16.44, "y":-5.0, "theta":180.0, },
    "poste4":{"x":13.31, "y":3.50, "theta":6.29, },
    "input":{"x":3.31, "y":-3.43, "theta":0.11, },
    # "output":{"x":43.19, "y":23.15, "theta":-91.35, },
    "output":{"x":40.66, "y":5.90, "theta":30.44, },
}

class Machine(threading.Thread):
    def __init__(self, threadID, factoryid, machineid, vitesse=1, temps=1, duree=10.0):
        # vitesse est un facteur multiplicatif de la vitesse
        # temps est le temps entre deux rafraichissements
        # durée est la durée de la tache de fabrication
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.machineid = machineid
        self.factoryid = factoryid
        whoiam = commandeAPI.getvalues(self.factoryid, "resource", self.machineid)
        # position = self.findrealposition(whoiam)
        position = commandeAPI.findrealposition(self.factoryid, whoiam)
        self.posx = position["x"]
        self.posy = position["y"]
        self.theta = position["theta"]
        self.vitesse = vitesse
        self.temps = temps
        self.listeoperation = []
        commandeAPI.updatestatus(self.factoryid, "machine", self.machineid, "free")
        self.running = True
        self.name = whoiam["name"]
        try:
            self.actiontime = whoiam["internalParams"]["actiontime"]
        except (KeyError, TypeError):
            self.actiontime = duree

    def run(self): # Première version : consomme beaucoup de bande passante, intérogation de chaque opération précédante
        print('running ' + self.name + ' simulated')
        while self.running:
            findOperation = commandeAPI.findINfactory(self.factoryid, "operation", status="toDo", resourceInfo=self.machineid)
            # if len(FindedUnseenOrder)>0:
            #traitement des todo
            for operationtodo in findOperation:
                allInfo = commandeAPI.getvalues(self.factoryid, "operation", operationtodo)
                runIt = True
                for operation in allInfo['precedenceOperationInfo']:
                    try:
                        if commandeAPI.getvalues(self.factoryid, "operation", operation)['status'] == 'done':
                            continue
                        else:
                            runIt = False
                            break
                    except commandeAPI.requests.Timeout:
                        runIt = False
                        break
                if runIt:
                    print("\nexecution de {}".format(allInfo["_id"]))
                    commandeAPI.updatestatus(self.factoryid, "operation", operationtodo, "doing")
                    commandeAPI.updatestatus(self.factoryid, "machine", self.machineid, "busy")
                    time.sleep(self.actiontime / self.vitesse)
                    print("\nexecution de {} effectuée".format(allInfo["_id"]))
                    commandeAPI.updatestatus(self.factoryid, "machine", self.machineid, "free")
                    commandeAPI.updatestatus(self.factoryid, "operation", operationtodo, "done")
                    break
                else:
                    self.listeoperation.append(allInfo["_id"])
                    commandeAPI.updatestatus(self.factoryid, "operation", operationtodo, "toDoAcknowledge")
                    print("\nexecution de {} impossible ==> Queued".format(allInfo["_id"]))
            #traitement des todoacknowledge
            for operationtodo in self.listeoperation:
                allInfo = commandeAPI.getvalues(self.factoryid, "operation", operationtodo)
                runIt = True
                for operation in allInfo['precedenceOperationInfo']:
                    try:
                        if commandeAPI.getvalues(self.factoryid, "operation", operation)['status'] == 'done':
                            continue
                        else:
                            runIt = False
                            break
                    except commandeAPI.requests.Timeout:
                        runIt = False
                        break
                if runIt:
                    print("\nexecution de Queued {} par {}".format(allInfo["_id"], self.threadID))
                    commandeAPI.updatestatus(self.factoryid, "operation", operationtodo, "doing")
                    commandeAPI.updatestatus(self.factoryid, "machine", self.machineid, "busy")
                    time.sleep(self.actiontime / self.vitesse)
                    print("\nexecution de Queued {} effectuée par {}".format(allInfo["_id"], self.threadID))
                    commandeAPI.updatestatus(self.factoryid, "machine", self.machineid, "free")
                    commandeAPI.updatestatus(self.factoryid, "operation", operationtodo, "done")
                    self.listeoperation.remove(operationtodo)
                    break
            print(self.threadID, end='', flush=True)
            time.sleep(self.temps)

    def terminate(self):
        print('end of ' + self.name + ' simulator')
        commandeAPI.updatestatus(self.factoryid, "machine", self.machineid, "offline")
        self.running = False

if __name__ == "__main__":
    Regeneration = False
    # factoryid = commandeAPI.findfactory(name="Factory LINEACT simulated")[0]
    if len(sys.argv) == 3:
        nom = sys.argv[2]
    else:
        nom = "Factory LINEACT Real"
    factoryid = commandeAPI.findfactory(name=nom)[0]
    #mir100_Arm mir100
    if Regeneration:
        for machine in commandeAPI.findINfactory(factoryid, typedata="resource", resourceType="Machine"): #on détruit les machines et leurs stocks
            for stock in commandeAPI.findINfactory(factoryid,typedata="stock",link="machine"):
                commandeAPI.deletepart(factoryid, typedata="stock", iddata=stock)
            commandeAPI.deletepart(factoryid, typedata="machine", iddata=machine)
        commandeAPI.deletepart(factoryid, typedata="operation", operationType="production")
        # commandeAPI.deletepart(factoryid, typedata="stock")                              # database stock Attention detruit aussi les stocks des agv



        json = commandeAPI.createStock(factoryid, "Stock Approvisionnement", "out", position2d=position["input"])
        stockappro = json["_id"]
        json = commandeAPI.createStock(factoryid, "Stock sortie", "in", position2d=position["output"])
        stockout = json["_id"]

        poste1 = commandeAPI.createPoste(factoryid, "Poste 1", position["poste1"])['poste']
        poste2 = commandeAPI.createPoste(factoryid, "Poste 2", position["poste2"])['poste']
        poste3 = commandeAPI.createPoste(factoryid, "Poste 3", position["poste3"])['poste']
        poste4 = commandeAPI.createPoste(factoryid, "Poste 4", position["poste4"])['poste']

        ope1 = commandeAPI.createOperationMachine(factoryid, poste1)["_id"]
        ope2 = commandeAPI.createOperationMachine(factoryid, poste2, previous=ope1)["_id"]
        ope3 = commandeAPI.createOperationMachine(factoryid, poste3)["_id"]
        ope4 = commandeAPI.createOperationMachine(factoryid, poste4, previous=[ope2, ope3])["_id"]

    else:
        poste1 = commandeAPI.findINfactory(factoryid, "resource", name="Poste 1")[0]
        poste2 = commandeAPI.findINfactory(factoryid, "resource", name="Poste 2")[0]
        poste3 = commandeAPI.findINfactory(factoryid, "resource", name="Poste 3")[0]
        poste4 = commandeAPI.findINfactory(factoryid, "resource", name="Poste 4")[0]

    machine1 = Machine(1, factoryid, poste1, vitesse=1, temps=1, duree=10.0)
    machine2 = Machine(2, factoryid, poste2, vitesse=1, temps=1, duree=10.0)
    machine3 = Machine(3, factoryid, poste3, vitesse=1, temps=1, duree=10.0)
    machine4 = Machine(4, factoryid, poste4, vitesse=1, temps=1, duree=10.0)
    machine1.start()
    machine2.start()
    machine3.start()
    machine4.start()

    print("done")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        machine1.terminate()
        machine2.terminate()
        machine3.terminate()
        machine4.terminate()
    print("killed")
