#!/usr/bin/env python2
# coding: utf8
# Copyright 2022 Fabrice DUVAL

from __future__ import unicode_literals
from __future__ import print_function
from ast import Global
from bdb import Breakpoint
# import xml.etree.ElementTree as ET
from lxml import etree as ET
import time
import sys
# import os
# import glob
import threading
# import imp
# import queue
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
    webdatabase = sys.argv[3]
except IndexError:
    webdatabase = "../../humains-web/BasedonneesHuman.xml"
print("Used databse: ", webdatabase)

runningtask = None

# functionlist = ["robotmove", "grab", "production", ]

class AgentTask(threading.Thread):
    """définition de l'agent gerant les taches"""
    def __init__(self, threadID, name, thefactoryid, resourcesid):
        """init"""
        threading.Thread.__init__(self)
        self.threadid = threadID
        self.name = name    # nom, non utilisé
        self.factoryid = thefactoryid
        self.mirrordatabase = {}
        self.status = "offline"
        self.runningmission = None
        self.runningtask = None
        self.taskdict={}
        self.operationlist=[]
        for resource in resourcesid:
            self.mirrordatabase[resource] = commandeAPI.getvalues(self.factoryid, "human", resource)
            commandeAPI.updatestatus(self.factoryid, "human", resource, "free")

        # self.updatepos()
        self.init()
        # self.updatexml()
        self.running = True
        self.forcednext = ''

    def init(self):
        """fix errors"""
        # fixe error in database
        parser = ET.XMLParser(remove_blank_text=True, encoding='utf-8')
        tree = ET.parse(webdatabase, parser)
        root = tree.getroot()
        root.attrib['factoryid'] = self.factoryid
        persons = root.findall('operator')

        for person in persons:
            root.remove(person)

        find_error_task = []
        for resource in self.mirrordatabase.keys():
            commandeAPI.updatestatus(self.factoryid, "human", resource, "free")
            find_error_task.extend(commandeAPI.findINfactory(self.factoryid, "task", status="toDoAcknowledge", resourceInfo=resource))
            find_error_task.extend(commandeAPI.findINfactory(self.factoryid, "task", status="doing", resourceInfo=resource))
            # create personne
            newop = ET.SubElement(root, 'operator',id=resource)
            # newop.set('id', resource)
            newop1 = ET.SubElement(newop, 'titre')
            newop1.text = self.mirrordatabase[resource]['name']

        # restore acknowledgment
        for atraiter in find_error_task:
            commandeAPI.updatestatus(self.factoryid, "task", atraiter, "toDo")

        with open(webdatabase, mode="w", encoding="utf-8") as f:
            f.write(ET.tostring(tree, pretty_print=True, xml_declaration=True, encoding = "utf-8").decode())


    # def conformoperator(self, person):
    #     enbase = self.mirrordatabase[person.attrib['id']]
    #     if not enbase["name"] == person.find('titre').text:
    #         return True

    def addtaskxml(self, taskid):
        # importing the module.
        # parsing directly.
        operator = self.taskdict[taskid][0]["resourceInfo"]
        parser = ET.XMLParser(remove_blank_text=True, encoding='utf-8')
        tree = ET.parse(webdatabase, parser)
        root = tree.getroot()
        # persons = root.findall('operator')
        operatorxml = root.xpath("//operator[@id = '%s']" % operator)
        if not operatorxml:
            return False
        operatorxml = operatorxml[0]

        basename = self.taskdict[taskid][0]["name"] + ": " + self.taskdict[taskid][0]["taskName"]
        # self.taskdict[taskid].append({})
        for i,text in enumerate(self.taskdict[taskid][0]["taskstodo"]):
            try:
                position = self.taskdict[taskid][0]["transform2D"]
                position = [position['x'], position['y'], position['theta'],]
            except:
                position = [0.0, 0.0, 0.0,]
            try:
                stockpos = self.taskdict[taskid][0]["stockInfo"]
                position.append(stockpos)
            except:
                pass
            newop = commandeAPI.createOperationHuman(self.factoryid, operator, position, [text], name=basename+'_'+str(i))
            self.taskdict[taskid][1][newop['_id']] = "standBy"
            newop1 = ET.SubElement(operatorxml,"operation", id = newop['_id'], valid="False")
            newop2 = ET.SubElement(newop1,"line_1")
            newop2.text = basename+'_'+str(i)
            newop2 = ET.SubElement(newop1,"line_2")
            newop2.text = text

        commandeAPI.updateobject(self.factoryid, "task", taskid, {"operationInfoList":list(self.taskdict[taskid][1].keys())})
        with open(webdatabase, mode="w", encoding="utf-8") as f:
            f.write(ET.tostring(tree, pretty_print=True, xml_declaration=True, encoding = "utf-8").decode())
        # parsing using the string.
        # print(root)
        return True

    def testtaskrunnable(self, valeur):
        """define if "valeur" task can be executed
        return True or False"""
        for pre_task in valeur['precedenceTaskInfo']:
            taskvaleur = commandeAPI.getstatus(self.factoryid, "task", pre_task)
            if taskvaleur != "done":
                return False
        #True, we need to push it !!
        return True

    def setopetodo(self,taskid, valeur):
        operator = valeur[0]["resourceInfo"]
        parser = ET.XMLParser(remove_blank_text=True, encoding='utf-8')
        tree = ET.parse(webdatabase, parser)
        root = tree.getroot()

        opebusy = False
        for ope in valeur[1].keys():
            operationxml = root.xpath("//operation[@id = '%s']" % ope)
            if not operationxml:
                print('operation invalid {}'.format(ope))
                return False
            else:
                opebusy = True
                operationxml[0].attrib['valid'] = 'True'
                commandeAPI.updatestatus(self.factoryid,"operation",ope,'toDo')
                valeur[1][ope] = "todo"
        if opebusy:
            commandeAPI.updatestatus(self.factoryid,"human",operator,'busy')
        else:
            print("nothing to do...")

        with open(webdatabase, mode="w", encoding="utf-8") as f:
            f.write(ET.tostring(tree, pretty_print=True, xml_declaration=True, encoding = "utf-8").decode())

    
    def testandsetmission(self, key, valeur):
        """return true if loop can continue
        test operation (key/value) and push it in fifo if possible"""
        if self.testtaskrunnable(valeur[0]):
            commandeAPI.updatestatus(self.factoryid, "resource", valeur[0]["resourceInfo"], "busy")
            commandeAPI.updatestatus(self.factoryid, "task", key, "doing")
            valeur[0]["status"] = "doing"
            self.setopetodo(key, valeur)
            return False
        return True
    
    def testalloperation(self, task, valeur):
        taskfinish = True
        change = False
        operator = valeur[0]["resourceInfo"]

        parser = ET.XMLParser(remove_blank_text=True, encoding='utf-8')
        tree = ET.parse(webdatabase, parser)
        root = tree.getroot()

        for key, status in valeur[1].items():
            if status == "todo":
                if commandeAPI.getstatus(self.factoryid, "operation", key) == "done":
                    operationxml = root.xpath("//operation[@id = '%s']" % key)
                    if not operationxml:
                        print('operation invalid {}'.format(key))
                        return False
                    else:
                        operationxml[0].attrib['valid'] = 'Finish'
                        valeur[1][key] = "done"
                        change = True
                else:
                    taskfinish = False
        if taskfinish:
            commandeAPI.updatestatus(self.factoryid, "task", task, "done")
            commandeAPI.updatestatus(self.factoryid, "operator", operator, "free")
            for key in valeur[1]:
                operationxml = root.xpath("//operation[@id = '%s']" % key)
                if not operationxml:
                    print('operation invalid {}'.format(key))
                    return False
                else:
                    operationxml[0].getparent().remove(operationxml[0])
            del(self.taskdict[task])

        if change:
            with open(webdatabase, mode="w", encoding="utf-8") as f:
                f.write(ET.tostring(tree, pretty_print=True, xml_declaration=True, encoding = "utf-8").decode())
        return taskfinish

    def run(self):
        """main task, loop until self.running"""
        while self.running:
            time.sleep(1.0)
            finded_unseen_task = commandeAPI.findINfactory(self.factoryid, "taskHuman", status="toDo")
            ### update self.operationlist (list of all runable operation)
            for atraiter in finded_unseen_task:
                commandeAPI.updatestatus(self.factoryid, "taskHuman", atraiter, "toDoAcknowledge")
                taskbase = commandeAPI.getvalues(self.factoryid, "taskHuman", atraiter) # quelle tache ? 
                self.taskdict[atraiter] = [taskbase, {},] # on update la liste interne
                if not self.addtaskxml(atraiter):
                    # erreur ==> resource inexistante
                    commandeAPI.updatestatus(self.factoryid, "taskHuman", atraiter, "error")
                    del(self.taskdict[atraiter])

            for key, valeur in self.taskdict.items():
                status = valeur[0]["status"]
                if status == "toDoAcknowledge":
                    self.testandsetmission(key, valeur)
                    time.sleep(0.2)
                elif status == "doing":
                    if self.testalloperation(key, valeur):
                        break
                    time.sleep(0.2)

            
    def terminate(self):
        """clean agent stop"""
        for resource in self.mirrordatabase.keys():
            commandeAPI.updatestatus(self.factoryid, "human", resource, "offline")
        print("agent task killed")
        self.running = False

if __name__ == "__main__":

    creationtest = False
    runtest = False

    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
    print("Launch Task Human Agent " + commandeAPI.urlTemplate)
    resources = commandeAPI.findINfactory(factoryid, "human")

    taskagent = AgentTask(1, nomfactory+" humans", factoryid, resources)
    # runningtask = TaskRunning(1, nomfactory+" humans", factoryid, resources)
    taskagent.runningtask = runningtask

    if creationtest or runtest:
        operatorid = commandeAPI.findINfactory(factoryid, "human", name="Operateur")[0]
        stockid = commandeAPI.findINfactory(factoryid, "stock", name="StockIntermediate")[0]

    if creationtest:
        productid = commandeAPI.createProduct(factoryid, "Raw_Part N_1", "Raw_Part")["_id"]
        taskid = commandeAPI.createTaskHuman(factoryid,"Tache D","Retournement","R_Intermediate_Part N_1",[],productid,["retourner la piece","fixer la piece"], position=(0,0,0,stockid), resource=operatorid)["_id"]
    else:
        if runtest:
            taskid = commandeAPI.findINfactory(factoryid, "taskHuman", name="Tache D")[0]
    
    if runtest:
        commandeAPI.updatestatus(factoryid, "task", taskid, "toDo")



    taskagent.start()

    print("done")
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        taskagent.terminate()
    print("killed")
