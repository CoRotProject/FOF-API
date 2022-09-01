import time
# import imp
import sys
# import queue
import json
# import mir
import Commandes.commandeAPI as commandeAPI
#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

try:
    nomfactory = sys.argv[2]
except IndexError:
    nomfactory = "Factory CERI"

try:
    nomrobot = sys.argv[3]
except IndexError:
    nomrobot = "CERI_META"

print("Factory : {}".format(nomfactory))
print("Robot : {}".format(nomrobot))


try:
    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
except IndexError:
    print("Base inacessible. Pause puis quitte")
    time.sleep(10)
    exit("Base non valide")

try:
    robot = commandeAPI.findINfactory(factoryid, "meta", name=nomrobot)[0]
except IndexError:
    print("robot {} inacessible. Pause puis quitte".format(nomrobot))
    time.sleep(10)
    exit("robot non valide")

class AgentTask():
    """définition de l'agent gerant les opérations des resources"""
    def __init__(self, name, factoryid, resourceid):
        self.name = name
        self.factoryid = factoryid
        self.resourceid = resourceid
        self.listtask = []
        self.currenttask = None
        self.currenttaskstatus = ""
        self.listoperation = []
        self.currentoperationindex = -1
        self.currentoperation = None
        self.currentoperationstatus = ""
        self.initialisation()
    
    def initialisation(self):
        self.listtask = commandeAPI.findINfactory(self.factoryid, "task", resourceInfo=self.resourceid, status="toDoAcknowledge")
        self.getTasks()

    def getTasks(self):
        listtask = commandeAPI.findINfactory(self.factoryid, "taskMoveProductXFromStockAToStockB", resourceInfo=self.resourceid, status="toDo")
        for task in listtask:
            commandeAPI.updatestatus(self.factoryid, "taskMoveProductXFromStockAToStockB", task, "toDoAcknowledge")
            self.listtask.append(task)
        return(self.listtask)
    
    def runNextTask(self):
        for task in self.getTasks():
            taskvalue = commandeAPI.getvalues(self.factoryid, "task", task)
            try:
                listprev = taskvalue["precedenceTaskInfo"]
            except KeyError:
                return self.startTask(task)
            
            previousOK = True
            for previous in listprev:
                if commandeAPI.getstatus(self.factoryid, "task", previous) == "done":
                    previousOK = True
                else:
                    previousOK = False
                    break
            
            if previousOK:
                return self.startTask(task)
        
        return None
    
    def startTask(self,tacheid):
        if self.currenttask:
            return None
        # create related operation
        self.currenttask = tacheid
        taskvalue = commandeAPI.getvalues(self.factoryid, "taskMoveProductXFromStockAToStockB", tacheid)
        try:
            name = taskvalue["name"] + "_"
        except KeyError:
            name = "task_"
        self.listoperation = []
        # move to A
        self.listoperation.append(commandeAPI.createOperationMoveRobotTo(self.factoryid, self.resourceid, (0, 0, 0, taskvalue["stockAInfo"]),name=name+"0")["_id"])
        # grab
        self.listoperation.append(commandeAPI.createOperationGrab(self.factoryid, self.resourceid, [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="grab", functionparameters=json.dumps({"nb_case":1}),name=name+"1", previous=self.listoperation[0])["_id"])
        # move to B
        self.listoperation.append(commandeAPI.createOperationMoveRobotTo(self.factoryid, self.resourceid, (0, 0, 0, taskvalue["stockBInfo"]), name=name+"1", previous=self.listoperation[1])["_id"])
        # ungrab
        self.listoperation.append(commandeAPI.createOperationGrab(self.factoryid, self.resourceid, [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="ungrab", functionparameters=json.dumps({"nb_case":1}),name=name+"3", previous=self.listoperation[2])["_id"])
        for num in range(4):
            commandeAPI.updatestatus(self.factoryid, "operation", self.listoperation[num], "toDoAcknowledge")
        commandeAPI.updateobject(self.factoryid, "taskMoveProductXFromStockAToStockB", tacheid,{"operationInfoList":commandeAPI.formalize2list(self.listoperation)})
        commandeAPI.updatestatus(self.factoryid, "taskMoveProductXFromStockAToStockB", tacheid, "doing")
        self.currenttaskstatus = "doing"

        return self.listoperation

    def startnextOperation(self):
        if not self.listoperation:
            return None
        if not self.currentoperation:
            self.currentoperation = self.listoperation[0]
            self.currentoperationindex = 0

        else:
            self.currentoperationindex = self.listoperation.index(self.currentoperation)
            if self.currentoperationstatus == "doing":
                commandeAPI.updatestatus(self.factoryid, "operation", self.listoperation[self.currentoperationindex], "done")
                self.currentoperationstatus == "done"
            try:
                self.currentoperation = self.listoperation[self.currentoperationindex+1]
                self.currentoperationindex += 1
            except IndexError:
                self.currentoperation = None
                self.currentoperationindex = -1
                self.currentoperationstatus = ""
                commandeAPI.updatestatus(self.factoryid, "taskMoveProductXFromStockAToStockB", self.currenttask, "done")
                self.listtask.remove(self.currenttask)
                self.currenttask = None
                self.currenttaskstatus = ""
                return None

        commandeAPI.updatestatus(self.factoryid, "operation", self.currentoperation, "doing")
        self.currentoperationstatus = "doing"
        return commandeAPI.getvalues(self.factoryid, "operation", self.currentoperation)
    
    def endcurrentOperation(self):
        if not self.listoperation:
            return False
        if not self.currentoperation:
            return False
        if self.currentoperationstatus == "doing":
            commandeAPI.updatestatus(self.factoryid, "operation", self.currentoperation, "done")
            self.currentoperationstatus = "done"
            return True
        elif self.currentoperationstatus == "error":
            commandeAPI.updatestatus(self.factoryid, "operation", self.currentoperation, "done")
            self.currentoperationstatus = "done"
            commandeAPI.updatestatus(self.factoryid, "taskMoveProductXFromStockAToStockB", self.currenttask, "doing")
            self.currenttaskstatus = "doing"
            return True
        return False
    
    def errorincurrentOperation(self):
        if not self.listoperation:
            return False
        if not self.currentoperation:
            return False
        if self.currentoperationstatus == "doing":
            commandeAPI.updatestatus(self.factoryid, "operation", self.currentoperation, "error")
            self.currentoperationstatus = "error"
            commandeAPI.updatestatus(self.factoryid, "taskMoveProductXFromStockAToStockB", self.currenttask, "error")
            self.currenttaskstatus = "error"
            return True
        return False

    def restorefailederror(self):
        if not self.listoperation:
            return None
        if not self.currentoperation:
            return None
        if self.currentoperationstatus == "error":
            commandeAPI.updatestatus(self.factoryid, "operation", self.currentoperation, "doing")
            self.currentoperationstatus = "doing"
            commandeAPI.updatestatus(self.factoryid, "taskMoveProductXFromStockAToStockB", self.currenttask, "doing")
            self.currenttaskstatus = "doing"
            return commandeAPI.getvalues(self.factoryid, "operation", self.currentoperation)
        return None
    
if __name__ == "__main__":
    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
    deleteope = True
    deletetask = True
    resetproduction = False
    test = True
    createvirtualpart = True


    print("Launch task Agent " + nomrobot + commandeAPI.urlTemplate)
    resource = commandeAPI.findINfactory(factoryid, "resource", name=nomrobot)[0]
    if deleteope:
        commandeAPI.deletepart(factoryid, typedata="operation", resourceInfo=resource)
    if deletetask:
        commandeAPI.deletepart(factoryid, typedata="taskMoveProductXFromStockAToStockB", resourceInfo=resource)
    
    if resetproduction:
        jsonout = commandeAPI.createProduct(factoryid, "RAWPART", "rawpart example")
        produit1 = jsonout["_id"]
        jsonout = commandeAPI.createStock(factoryid, "stockfrom", "out", position2d={"x":5.0, "y":5.0, "theta":0.0, })
        stockAId = jsonout["_id"]
        jsonout = commandeAPI.createStock(factoryid, "stockto", "in", position2d={"x":0.0, "y":0.0, "theta":0.0, })
        stockBId = jsonout["_id"]
    else:
        produit1 = commandeAPI.findINfactory(factoryid, "product", name="RAWPART")[0]
        stockAId = commandeAPI.findINfactory(factoryid, "stock", name="stockfrom")[0]
        stockBId = commandeAPI.findINfactory(factoryid, "stock", name="stockto")[0]

    if test:
        jsonout = commandeAPI.createTaskMoveProductXFromStockAToStockB(factoryid, "Move Task 1", produit1, stockAId, stockBId)
        taskid1 = jsonout["_id"]
        commandeAPI.updateobject(factoryid, "taskMoveProductXFromStockAToStockB", taskid1,{"resourceInfo":resource})
        commandeAPI.updateobject(factoryid, "product", produit1,{"link":stockAId})

        taches = AgentTask("CERA_META_tache", factoryid, resource)
        print(taches.currentoperationindex)
        print(taches.getTasks())
        commandeAPI.updatestatus(factoryid, "taskMoveProductXFromStockAToStockB", taskid1, "toDo")
        print(taches.currentoperationindex)
        print(taches.getTasks())
        print(taches.currentoperationindex)
        listoperation = taches.runNextTask()
        print(taches.currentoperationindex)
        print(taches.startnextOperation()) # op 1
        print(taches.currentoperationindex)
        print(taches.startnextOperation()) # op 2
        print(taches.currentoperationindex)
        print(taches.errorincurrentOperation()) # fail op2
        print(taches.currentoperationindex)
        print(taches.endcurrentOperation()) # ok op2
        print(taches.currentoperationindex)
        print(taches.startnextOperation())  # op 3
        print(taches.currentoperationindex)
        print(taches.errorincurrentOperation()) # fail op3
        print(taches.currentoperationindex)
        print(taches.restorefailederror()) # restaure op3
        print(taches.currentoperationindex)
        print(taches.startnextOperation()) # op4
        print(taches.currentoperationindex)
        print(taches.startnextOperation()) # fail no more task
        print(taches.currentoperationindex)


    print("killed")