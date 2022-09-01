import time
import sys
import TaskAgent
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

try:
    nomporte = sys.argv[4]
except IndexError:
    nomporte = "PorteCNC"
print("Used resource: ", nomporte)

runningtask = None

class TaskCERI_META(TaskAgent.TaskRunning):
    def __init__(self, threadID, name, thefactoryid, mainresourceid, porteid):
        TaskAgent.TaskRunning.__init__(self, threadID, name, thefactoryid, mainresourceid)
        self.porteid = porteid

    def tasktooperation(self,taskid, taskcontent):
        if self.validoperations:
            return False
        switchvalue = taskcontent["taskType"]
        self.operationlist = []
        if switchvalue == "Task":
            print("generictask")
        elif switchvalue == "taskProduce":
            print("produce")
        elif switchvalue == "taskMoveProductXFromStockAToStockB":
            taskfine = commandeAPI.getvalues(self.factoryid,"taskMoveProductXFromStockAToStockB",taskid)
            positionA = commandeAPI.getvalues(self.factoryid,"stock",taskfine["stockAInfo"])
            positionB = commandeAPI.getvalues(self.factoryid,"stock",taskfine["stockBInfo"])
            productid = commandeAPI.findINfactory(self.factoryid,"product",link=taskfine["stockAInfo"])[0]
            self.operationlist.append(["", "takelock"])
            self.operationlist.append([commandeAPI.createOperationMoveRobotTo(self.factoryid, self.resource, (0, 0, 0, taskfine["stockAInfo"]),name=taskcontent["name"]+"_1")["_id"],
                                        "robotmove", (0, 0, 0, taskfine["stockAInfo"])])
            self.operationlist.append([commandeAPI.createOperationGrab(self.factoryid, self.resource, [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="takefrom"+positionA["name"], name=taskcontent["name"]+"_2", previous=self.operationlist[-1][0])["_id"],
                                        "grab", [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]], "takefrom"+positionA["name"], {}])
            self.operationlist.append(["", "moveproduct", productid, self.resource])
            self.operationlist.append([commandeAPI.createOperationMoveRobotTo(self.factoryid, self.resource, (0, 0, 0, taskfine["stockBInfo"]),name=taskcontent["name"]+"_3", previous=self.operationlist[-1][0])["_id"],
                                        "robotmove", (0, 0, 0, taskfine["stockBInfo"])])
            self.operationlist.append([commandeAPI.createOperationGrab(factoryid, self.resource, [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]], fonctionrobot="putto"+positionB["name"], name=taskcontent["name"]+"_4", previous=self.operationlist[-1][0])["_id"],
                                        "grab", [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]], "putto"+positionB["name"], {}])
            self.operationlist.append(["", "moveproduct", productid, taskfine["stockBInfo"]])
            self.operationlist.append(["", "releaselock"])
            listeope = [self.operationlist[n][0] for n in [1, 2, 4, 5]]
            commandeAPI.updateobject(self.factoryid, "task", taskid, {"operationInfoList":listeope})

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
        if operation[1] == 'moveproduct':
            commandeAPI.updateobject(self.factoryid, "product", operation[2], {"link":operation[3]})
            return True
        elif operation[1] == 'robotmove':
            togoto = commandeAPI.getvalues(self.factoryid,"stock",operation[2][3])
            print('moveto ' + togoto['name'] + ' 1s')
            time.sleep(1)
            return True
        elif operation[1] == 'grab':
            if "CNC" in operation[3]:
                print('grab function with door ' + operation[3])
            else:
                print('grab function ' + operation[3])
            time.sleep(1)
            return True
        elif operation[1] == 'takelock':
            while not commandeAPI.takereservation(self.factoryid,self.porteid, self.resource):
                time.sleep(1.0)
        elif operation[1] == 'releaselock':
            commandeAPI.releasereservation(self.factoryid,self.porteid, self.resource)
        return False

if __name__ == "__main__":

    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
    Regeneration = False
    print("Launch Task Agent " + nommeta + commandeAPI.urlTemplate)
    resource = commandeAPI.findINfactory(factoryid, "resource", name=nommeta)[0]
    portecnc = commandeAPI.findINfactory(factoryid, "resource", name=nomporte)[0]

    taskagent = TaskAgent.AgentTask(1, nomfactory+" "+nommeta, factoryid, resource)
    runningtask = TaskCERI_META(1, nomfactory+" "+nommeta, factoryid, resource, portecnc)
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
