#!/usr/bin/env python2
# coding: utf8
# Copyright 2020 Fabrice DUVAL

from __future__ import unicode_literals
from __future__ import print_function
import time
import sys
# import os
import glob
import threading
# import imp
import queue
from FOF_API.Commandes import commandeAPI
#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

### Agent de lecture des operations correspondantes à une resources d'une usine => création d'une FIFO d'opération valide 

nomfactory = "Factory LINEACT Test Fabrice"
functionlist = ["robotmove", "grab", "production", ]

class AgentOperation(threading.Thread):
    """définition de l'agent gerant les opérations des resources"""
    def __init__(self, threadID, name, thefactoryid, resourceid, nomrep, liste_fonctions, fifooperation, fiforetour):
        """init : nomrep, directory of specifical function
        fifooperation : as output list of validated operation ; fiforetour : as input of retour from operation"""
        threading.Thread.__init__(self)
        self.threadid = threadID
        self.name = name    # nom, non utilisé
        self.factoryid = thefactoryid
        self.dirscripts = nomrep
        self.resoucebase = resourceid
        self.functionlist = liste_fonctions
        self.operations = fifooperation # FIFO of valid action
        self.retourresource = fiforetour # FIFO retour resource
        self.capability = []
        self.scripts = {}
        self.operationlist = {}
        self.status = "offline"
        self.nbrunningmission = 0

        self.mirrordatabase = commandeAPI.getvalues(self.factoryid, "resource", self.resoucebase)
        self.resourcetype = self.mirrordatabase['resourceType']

        commandeAPI.updatestatus(self.factoryid, self.resourcetype, self.resoucebase, "free")
        # self.updatepos()
        self.initfunctions()
        self.running = True
        self.forcednext = ''

    def initfunctions(self):
        """init list of habilities"""
        listescript = glob.glob(self.dirscripts+'/*.ascript')
        # suppression de toutes les anciennes capability
        # self.me_in_database["resourceCapabilityList"]
        listfonction = [x['category'] for x in self.mirrordatabase["resourceCapabilityList"] if 'category' in x.keys()]
        change = False
        for script in listescript:
            newscript = script[script.replace('\\', '/').rfind('/')+1:script.rfind('.')]
            self.scripts.update({newscript:script})
            #(re)creation des capabality
            if newscript not in listfonction:
                self.mirrordatabase["resourceCapabilityList"].append({'category':newscript})
        if change:
            commandeAPI.updateobject(self.factoryid, self.resourcetype, self.resoucebase, {"resourceCapabilityList":self.mirrordatabase["resourceCapabilityList"]})
        # [{"category": "transport"}, {"category": "wait"}]

        # fixe error in database
        find_error_operation = commandeAPI.findINfactory(self.factoryid, "operation", status="toDoAcknowledge", resourceInfo=self.resoucebase)
        # restore acknowledgment
        for atraiter in find_error_operation:
            commandeAPI.updatestatus(self.factoryid, "operation", atraiter, "toDo")

    def testoperationrunnable(self, valeur):
        """define if "valeur" operation can be executed
        return True or False"""
        for pre_operation in valeur['precedenceOperationInfo']:
            operation = commandeAPI.getvalues(self.factoryid, "operation", pre_operation)
            if operation['status'] != "done":
                return False
        #True, we need to push it !!
        return True

    def testandsetmission(self, key, valeur):
        """return true if loop can continue
        test operation (key/value) and push it in fifo if possible"""
        if self.testoperationrunnable(valeur):
            self.nbrunningmission += 1 # another running mission
            self.operations[valeur['operationType']].put([key, valeur])
            commandeAPI.updatestatus(self.factoryid, self.resourcetype, self.resoucebase, "busy")
            del self.operationlist[key]         
            if 'nextOperationInfo' in valeur and valeur['nextOperationInfo']:
                self.forcednext = valeur['nextOperationInfo']
            else:
                self.forcednext = ''
            return False
        return True

    def run(self):
        """main task, loop until self.running"""
        while self.running:
            finded_unseen_operation = commandeAPI.findINfactory(self.factoryid, "operation", status="toDo", resourceInfo=self.resoucebase)
            ### update self.operationlist (list of all runable operation)
            for atraiter in finded_unseen_operation:
                commandeAPI.updatestatus(self.factoryid, "operation", atraiter, "toDoAcknowledge")
                operationbase = commandeAPI.getvalues(self.factoryid, "operation", atraiter) # quelle operation ? 
                if operationbase['operationType'] in self.functionlist: # only valid action
                    self.operationlist[atraiter] = operationbase # on update la liste interne
                else: # sinon erreur
                    commandeAPI.updatestatus(self.factoryid, "operation", atraiter, "error")
            
            ### unsecable operation ?
            if self.forcednext:
                if self.forcednext in self.operationlist:
                    valeur = self.operationlist[self.forcednext]
                    self.testandsetmission(self.forcednext, valeur)
            else:
                #no linked operation... look in operation
                for key, valeur in self.operationlist.items():
                    # any runnable operation ?
                    if not self.testandsetmission(key, valeur):
                        #présence d'une operation valide => changement d'état de la liste => il faut sortir
                        break
            
            for retour in self.retourresource.values():
                if not retour.empty():
                    messagetobase = retour.get()
                    commandeAPI.updatestatus(self.factoryid, "operation", messagetobase[0], messagetobase[1])
                    if messagetobase[1] in ["done", "error"]:
                        self.nbrunningmission -= 1
                    if self.nbrunningmission == 0:
                        commandeAPI.updatestatus(self.factoryid, self.resourcetype, self.resoucebase, "free")
                    retour.task_done()
            time.sleep(1)

    def terminate(self):
        """clean agent stop"""
        commandeAPI.updatestatus(self.factoryid, self.resourcetype, self.resoucebase, "offline")
        print("agent op killed")
        self.running = False

class validateopminimal(threading.Thread):
    """définition de l'agent gerant les opérations des resources"""
    def __init__(self, threadID, name, fifooperation, fiforetour):
        """init : nomrep, directory of specifical function
        fifooperation : as output list of validated operation ; fiforetour : as input of retour from operation"""
        threading.Thread.__init__(self)
        self.threadid = threadID
        self.name = name    # nom, non utilisé
        self.operations = fifooperation # FIFO of valid action
        self.operationencours = None
        self.retourresource = fiforetour # FIFO retour resource
        self.running = True
        self.status = 'free'

    def run(self):
        """main task, loop until self.running"""
        nbturn = 0
        while self.running:
            if self.operations.empty():
                if nbturn == 1:
                    print("free_{}".format(self.threadid)) # on affiche l'état que tous les 20 tours pour limiter les infos inutiles
                elif nbturn >= 20:
                    nbturn = 0
            else:
                self.status = 'busy'
                self.operationencours = self.operations.get()
                self.retourresource.put((self.operationencours[0], 'doing'))
                print("action en cours_{}".format(self.threadid))
                print(self.operationencours)
                time.sleep(3) # action = wait 3s
                self.retourresource.put((self.operationencours[0], 'done'))
                self.operations.task_done()

            nbturn += 1
            time.sleep(1)

    def terminate(self):
        """clean agent stop"""
        print("agent action light killed")
        self.running = False

def testmove():
    # factoryid = commandeAPI.findfactory(name="Factory LINEACT Test Fabrice")[0]
    robot = commandeAPI.findINfactory(factoryid, "robot", name="mir100_Arm")[0]
    a1 = commandeAPI.createOperationMoveRobotTo(factoryid, robot, (0, 0, 0))["_id"]
    a2 = commandeAPI.createOperationMoveRobotTo(factoryid, robot, (12, 12, 45),previous=a1)["_id"]
    a3 = commandeAPI.createOperationMoveRobotTo(factoryid, robot, (12, 0, 78),previous=a1)["_id"]
    a4 = commandeAPI.createOperationMoveRobotTo(factoryid, robot, (0, 12, 156),previous=a1)["_id"]
    commandeAPI.updateobject(factoryid, "operation", a1, {"nextOperationInfo":a4})
    for operation in commandeAPI.findINfactory(factoryid, "operation", status="standBy"):
        commandeAPI.updatestatus(factoryid, "operation", operation, "toDo")

if __name__ == "__main__":

    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
    nom = "mir100_Arm"
    Regenerationope = False
    print("Launch Operation Agent " + nom + commandeAPI.urlTemplate)
    resource = commandeAPI.findINfactory(factoryid, "resource", name=nom)[0]
    if Regenerationope:
        commandeAPI.deletepart(factoryid, typedata="operation", resourceInfo=resource)
        testmove()

    fiforobotmove = queue.Queue() # create FIFO of valide operation
    fiforetrobotmove = queue.Queue() # create FIFO of return value for database
    fifograb = queue.Queue() # create FIFO of valide operation
    fiforetgrab = queue.Queue() # create FIFO of return value for database
    fifoproduction = queue.Queue() # create FIFO of valide operation
    fiforetproduction = queue.Queue() # create FIFO of return value for database
    fifoop = {"robotmove":fiforobotmove, "grab":fifograb, "production":fifoproduction, }
    fiforet = {"robotmove":fiforetrobotmove, "grab":fiforetgrab, "production":fiforetproduction, }

    opagent = AgentOperation(1, nomfactory+" "+nom, factoryid, resource, nom, functionlist, fifoop, fiforet)
    fictifagentrobotmove = validateopminimal(2, "fausse action move", fifoop["robotmove"], fiforet["robotmove"])
    fictifagentgrab = validateopminimal(3, "fausse action grab", fifoop["grab"], fiforet["grab"])
    fictifagentproduction = validateopminimal(4, "fausse action product", fifoop["production"], fiforet["production"])

    opagent.start()
    fictifagentrobotmove.start()
    fictifagentgrab.start()
    fictifagentproduction.start()
    print("done")
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        opagent.terminate()
        fictifagentrobotmove.terminate()
        fictifagentgrab.terminate()
        fictifagentproduction.terminate()
    print("killed")
