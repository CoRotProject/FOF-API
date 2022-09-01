import time
import sys
# import os
import glob
import threading
import CNC
import Commandes.commandeAPI as commandeAPI
#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

print("Test at CERI")

machinereel = CNC.CNC()
if len(sys.argv) > 1:
    nom = sys.argv[1]
else:
    nom = "Usinage_CERI"

position = {
    "poste1":{"x":36.25, "y":2.09, "theta":138.4, },
    "poste2":{"x":33.00, "y":-2.40, "theta":135.1, },
    "poste3":{"x":16.44, "y":-5.0, "theta":180.0, },
    "poste4":{"x":15.00, "y":3.50, "theta":6.29, },
    "input":{"x":3.31, "y":-3.43, "theta":0.11, },
    "output":{"x":43.19, "y":23.15, "theta":-91.35, },
    # "output":{"x":40.66, "y":5.90, "theta":30.44, },
}

class CNC(threading.Thread):
    """définition de l'agent gerant les opérations de la CNC"""
    def __init__(self, threadID, name, factoryId, myself, dirscripts, machinereelle):
        threading.Thread.__init__(self)
        self.threadid = threadID
        self.name = name
        self.myself = myself
        self.factoryid = factoryId
        self.dirscripts = dirscripts
        self.machine = machinereelle
        self.me_in_database = commandeAPI.getvalues(self.factoryid, "resource", myself)
        self.categories = [x['category'] for x in self.me_in_database["resourceCapabilityList"] if 'category' in x.keys()]
        for category in self.me_in_database["resourceCapabilityList"]:
            if 'category' in category.keys():
                self.categories.append(category['category'])

        if {'category':'production'} in self.me_in_database["resourceCapabilityList"]:
            self.initfunctionsproduct()
        self.operationlist = {} # liste des opérations à faire
        self.running = True

    def initfunctionsproduct(self):
        listeprog = self.machine.getprograms()
        self.scripts = {}
        # suppression de toutes les anciennes capability
        # self.me_in_database["resourceCapabilityList"]
        listfonction = [x['category'] for x in self.me_in_database["resourceCapabilityList"] if 'category' in x.keys()]
        for programme in listeprog:
            #(re)creation des capabality
            if programme not in listfonction:
                self.me_in_database["resourceCapabilityList"].append({'category':programme})
        commandeAPI.updateobject(self.factoryid, "resource", self.myself, {"resourceCapabilityList":self.me_in_database["resourceCapabilityList"]})
        # [{"category": "transport"}, {"category": "wait"}]
        return

    def testoperationrunnable(self, opevaleur):
        # return if operation "opevaleur" can be executed
        for pre_operation in opevaleur['precedenceOperationInfo']:
            operation = commandeAPI.getvalues(self.factoryid, "operation", pre_operation)
            if operation['status'] != "done":
                return False
        return True

    def run(self):
        while self.running:
            finded_unseen_operation = commandeAPI.findINfactory(self.factoryid, "operation", status="toDo", resourceInfo=self.myself)
            for atraiter in finded_unseen_operation:
                commandeAPI.updatestatus(self.factoryid, "operation", atraiter, "toDoAcknowledge")
                operationbase = commandeAPI.getvalues(self.factoryid, "operation", atraiter)
                if operationbase['operationType'] == "production":
                    operationtodo = operationbase['params']['function']
                    if operationtodo not in self.scripts.keys() and not operationtodo == 'production' and not operationtodo == 'wait':
                        commandeAPI.updatestatus(self.factoryid, "operation", atraiter, "error") # je ne sais pas faire
                    else:
                        self.operationlist[atraiter] = operationbase # on update la liste interne

            for key, valeur in self.operationlist.items():
                if self.testoperationrunnable(valeur):
                    # on lance cette opération
                    # a valider ici
                    commandeAPI.updatestatus(self.factoryid, "operation", atraiter, "doing")
                    # quand c'est fait : on le dit
                    # robot.sendcommand("ur5_t_e\\grab.ascript", delta_saisie=0.10)
                    if operationtodo in self.scripts.keys():
                        self.machine.run(self.scripts[operationtodo])
                        # wait end of production here !
                        print("running op {}".format(self.scripts[operationtodo]))
                    elif operationtodo == 'production':
                        print("production")
                    elif operationtodo == 'wait':
                        print("wait")
                    commandeAPI.updatestatus(self.factoryid, "operation", atraiter, "done")
                else:
                    # si non ==> on informe la base
                    commandeAPI.updatestatus(self.factoryid, "operation", atraiter, "error")
            time.sleep(1)

    def terminate(self):
        commandeAPI.updatestatus(self.factoryid, "machine", self.machine, "offline")
        self.running = False

if __name__ == "__main__":
    Regeneration = True # régénération de la liste d'opération
    print("Launch Machine Agent " + nom + " connected to database " + commandeAPI.urlTemplate)
    factoryid = commandeAPI.findfactory(name="Factory CERI")[0]
    if Regeneration:
        machine = commandeAPI.findINfactory(factoryid, "machine", name=nom)
        if machine:
            machine = machine[0]
            commandeAPI.deletepart(factoryid, typedata="operation", resourceInfo=machine)
    else:
        machine = commandeAPI.findINfactory(factoryid, "machine", name=nom)[0]

    machine_agent = CNC(1, "Machine agent CERI", factoryid, machine, nom, machinereel)

    operationMachine1 = commandeAPI.createOperationMachine(factoryid, machine, name="Machine 1-1")["_id"]
    operationMachine2 = commandeAPI.createOperationMachine(factoryid, machine, name="Machine 1-2", previous=operationMachine1)["_id"]
    operationMachine3 = commandeAPI.createOperationMachine(factoryid, machine, name="Machine 1-3", previous=operationMachine2)["_id"]

    commandeAPI.updatestatus(factoryid, "operation", operationMachine1, "toDo")
    commandeAPI.updatestatus(factoryid, "operation", operationMachine2, "toDo")
    commandeAPI.updatestatus(factoryid, "operation", operationMachine3, "toDo")

    machine_agent.start()
    print("done")
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        machine_agent.terminate()
    print("killed")