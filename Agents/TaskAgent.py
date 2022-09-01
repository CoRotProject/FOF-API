#!/usr/bin/env python2
# coding: utf8
# Copyright 2022 Fabrice DUVAL

from __future__ import unicode_literals
from __future__ import print_function
from ast import Global
from bdb import Breakpoint
import time
import sys
# import os
# import glob
import threading
# import imp
import queue
import Commandes.commandeAPI as commandeAPI
#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

### Agent de lecture des operations correspondantes à une resources d'une usine => création d'une FIFO d'opération valide 

try:
    nomfactory = sys.argv[2]
except IndexError:
    nomfactory = "Factory LINEACT Test Fabrice"
print("Used factory: ", nomfactory)

try:
    nommeta = sys.argv[3]
except IndexError:
    nommeta = "CERI_META"
print("Used resource: ", nommeta)

runningtask = None

# functionlist = ["robotmove", "grab", "production", ]

class TaskRunning(threading.Thread):
    """définition de l'agent gerant les taches"""
    def __init__(self, threadID, name, thefactoryid, mainresourceid):
        """init"""
        threading.Thread.__init__(self)
        self.threadid = threadID
        self.name = name    # nom, non utilisé
        self.factoryid = thefactoryid
        self.resource = mainresourceid # Meta resource id
        self.currenttaskid = None
        self.currenttaskcontent = None
        self.running = True
        self.status = None
        self.operationlist = []
        self.validoperations = False

    def newtask(self,taskid, taskcontent):
        if self.currenttaskid:
            return False
        else:
            self.currenttaskid = taskid
            self.currenttaskcontent = taskcontent
            return self.tasktooperation(taskid, taskcontent)

    def tasktooperation(self,taskid, taskcontent):
        switchvalue = taskcontent["taskType"]

        if switchvalue == "Task":
            print("generictask")
        elif switchvalue == "taskProduce":
            print("produce")
        elif switchvalue == "taskMoveProductXFromStockAToStockB":
            print("MoveProductXFromStockAToStockB")
        elif switchvalue == "taskHuman":
            print("Human")

        retour = False
        for operation in self.operationlist:
            if operation[0]:
                commandeAPI.updatestatus(factoryid, "operation", operation[0], "toDo")
            retour = True

        self.validoperations = retour
        return retour
    
    def operation(self,operation):
        if operation[1] == 'robotmove':
            print('moveto... 1s')
            time.sleep(1)
        elif operation[1] == 'grab':
            print('grab function ' + operation[3])
            time.sleep(1)
        return True

    def getstatus(self):
        return self.status
    
    def resetstatus(self):
        self.status = "free"
        return True

    def run(self):
        """main task, loop until self.running"""
        self.status = "free"
        while self.running:
            if not self.validoperations:
                self.status = "free"
                time.sleep(1)
                continue
            for ope in self.operationlist:
                self.status = "busy"
                if ope[0]:
                    commandeAPI.updatestatus(self.factoryid,'operation',ope[0],"doing")
                    if self.operation(ope):
                        commandeAPI.updatestatus(self.factoryid,'operation',ope[0],"done")
                    else:
                        commandeAPI.updatestatus(self.factoryid,'operation',ope[0],"error")
                        self.status = "error"
                else:
                    self.operation(ope)
            self.operationlist=[]
            self.validoperations = False
            self.currenttaskid = None
            self.currenttaskcontent = None

    def terminate(self):
        """clean agent stop AA"""
        # commandeAPI.updatestatus(self.factoryid, self.resourcetype, self.resourcebase, "offline")
        print("agent running task killed")
        self.running = False

class AgentTask(threading.Thread):
    """définition de l'agent gerant les taches"""
    def __init__(self, threadID, name, thefactoryid, resourceid):
        """init"""
        threading.Thread.__init__(self)
        self.threadid = threadID
        self.name = name    # nom, non utilisé
        self.factoryid = thefactoryid
        self.resourceid = resourceid # Meta resource id
        self.capability = []
        self.status = "offline"
        self.runningmission = None
        self.runningtask = None
        self.tasklist={}
        self.operationlist=[]
        if resourceid:
            self.mirrordatabase = commandeAPI.getvalues(self.factoryid, "resource", self.resourceid)
        else:
            self.mirrordatabase = None
        self.resourcetype = self.mirrordatabase['resourceType'] # Must be a META resource for movement

        commandeAPI.updatestatus(self.factoryid, self.resourcetype, self.resourceid, "free")
        try:
            self.compositionid = self.mirrordatabase["composition"]
        except KeyError:
            self.compositionid = self.resourceid
            self.compositiondata = self.mirrordatabase
        else:
            self.compositiondata = {}
            for resource in self.mirrordatabase["composition"]:
                commandeAPI.updatestatus(self.factoryid, "resource", resource, "in_meta")
                self.compositiondata[resource] = commandeAPI.getvalues(self.factoryid, "resource", resource)

        # self.updatepos()
        self.init()
        self.running = True
        self.forcednext = ''

    def init(self):
        """fix errors"""
        # fixe error in database
        find_error_task = commandeAPI.findINfactory(self.factoryid, "task", status="toDoAcknowledge", resourceInfo=self.resourceid)
        find_error_task.extend(commandeAPI.findINfactory(self.factoryid, "task", status="doing", resourceInfo=self.resourceid))
        # restore acknowledgment
        for atraiter in find_error_task:
            commandeAPI.updatestatus(self.factoryid, "task", atraiter, "toDo")

    def testtaskrunnable(self, valeur):
        """define if "valeur" task can be executed
        return True or False"""
        for pre_task in valeur['precedenceTaskInfo']:
            taskvaleur = commandeAPI.getstatus(self.factoryid, "task", pre_task)
            if taskvaleur != "done":
                return False
        #True, we need to push it !!
        return True

    def testandsetmission(self, key, valeur):
        """return true if loop can continue
        test operation (key/value) and push it in fifo if possible"""
        if self.testtaskrunnable(valeur):
            self.runningmission = key # another running mission
            commandeAPI.updatestatus(self.factoryid, "resource", self.resourceid, "busy")
            commandeAPI.updatestatus(self.factoryid, "task", key, "doing")
            print("running task")
            # execution de la tache "valeur"
            self.runningtask.newtask(key, valeur)
            time.sleep(1.0)
            return False
        return True

    def run(self):
        """main task, loop until self.running"""
        while self.running:
            finded_unseen_task = commandeAPI.findINfactory(self.factoryid, "task", status="toDo", resourceInfo=self.resourceid)
            ### update self.operationlist (list of all runable operation)
            for atraiter in finded_unseen_task:
                commandeAPI.updatestatus(self.factoryid, "task", atraiter, "toDoAcknowledge")
                taskbase = commandeAPI.getvalues(self.factoryid, "task", atraiter) # quelle tache ? 
                self.tasklist[atraiter] = taskbase # on update la liste interne
            if not self.runningmission:
                # print("look for new validated task")                     
                # look in task list
                for key, valeur in self.tasklist.items():
                    # any runnable task ?
                    if not self.testandsetmission(key, valeur):
                        #présence d'une tache valide => changement d'état de la liste => il faut sortir
                        break
            elif self.runningtask.getstatus() == 'free':
                print("runnig task free")
                if self.runningmission:
                    print("it's finish")
                    # supprimer la tache de la liste, réinialiser la bdd
                    commandeAPI.updatestatus(self.factoryid, "task", self.runningmission, "done")
                    del self.tasklist[self.runningmission]
                    self.runningmission = None
                    commandeAPI.updatestatus(self.factoryid, self.resourcetype, self.resourceid, "free")
            time.sleep(1.0)

    def terminate(self):
        """clean agent stop"""
        commandeAPI.updatestatus(self.factoryid, self.resourcetype, self.resourceid, "offline")
        try:
            for resource in self.mirrordatabase["composition"]:
                commandeAPI.updatestatus(self.factoryid, "resource", resource, "offline")
        except KeyError:
            print("It's not a meta")
        print("agent task killed")
        self.running = False

if __name__ == "__main__":

    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
    nom = "CERI_META"
    Regeneration = False
    print("Launch Task Agent " + nom + commandeAPI.urlTemplate)
    resource = commandeAPI.findINfactory(factoryid, "resource", name=nom)[0]

    taskagent = AgentTask(1, nomfactory+" "+nom, factoryid, resource)
    runningtask = TaskRunning(1, nomfactory+" "+nom, factoryid, resource)
    taskagent.runningtask = runningtask

    taskagent.start()
    runningtask.start()
    print("done")
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        taskagent.terminate()
        runningtask.terminate()
    print("killed")
