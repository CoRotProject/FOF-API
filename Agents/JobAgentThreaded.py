import time
import sys
# import requests
# import pymongo
import threading
sys.path.append("..\\Commandes")
from Commandes.commandeAPI import deletepart, findfactory, findINfactory, createProduct, createTaskMoveProductXFromStockAToStockB,\
   defineNewJob, createJob, createStock, updatestatus, getvalues, duplicatetask, updateobject, formalize2list

class AgentJobToTaskClass(threading.Thread):
    """définition de l'agent transformant les jobs en taches"""
    def __init__(self, threadID, name, factoryId):
        threading.Thread.__init__(self)
        self.threadid = threadID
        self.name = name
        self.factoryid = factoryId
        self._running = True
    def run(self):
        while self._running:
            finded_unseen_job = findINfactory(self.factoryid, "job", jobStatus="toDo")
            for atraiter in finded_unseen_job:
                updatestatus(self.factoryid, "job", atraiter, "toDoAcknowledge")
                jobbase = getvalues(self.factoryid, "job", atraiter)
                findtasklist = findINfactory(self.factoryid, "jobdescription", name=jobbase["productToDo"])
                if findtasklist:
                    tasktoduplicate = getvalues(self.factoryid, "jobdescription", findtasklist[0])["taskList"]
                    tasklist = []
                    for task in tasktoduplicate:
                        tasklist.append(duplicatetask(self.factoryid, task, jobbase["name"], named=True)["_id"])
                    updateobject(self.factoryid, "job", atraiter, {"taskList":formalize2list(tasklist)})
                else:
                    updatestatus(self.factoryid, "job", atraiter, "unknown")
                # listejob=[]
                # for a in range(Ordrebase["quantity"]):
                #     listejob.append(createJob(self.factoryid, Ordrebase["name"]+"_{:06}".format(a+1), Ordrebase["productToDo"])["_id"])
                # updateobject(self.factoryid, "order", achanger, {"jobList": listejob})
                # updatestatus(self.factoryid, "order", achanger, "toDoSplitedIntoJobs")
            time.sleep(1)
    def stop(self):
        self._running = False


if __name__ == "__main__":
    Regeneration = True
    factoryidentity = findfactory(name="Factory LINEACT Test Fabrice")[0]
    if Regeneration:
        deletepart(factoryidentity, typedata="job")
        deletepart(factoryidentity, typedata="jobdescription", name="iPhone 10")
        deletepart(factoryidentity, typedata="product", name="iPhone 10 RAWPART")
        deletepart(factoryidentity, typedata="stock", name="Stock A")
        deletepart(factoryidentity, typedata="stock", name="Stock B")
        deletepart(factoryidentity, typedata="stock", name="Machine A Stock in 1")
        deletepart(factoryidentity, typedata="stock", name="Machine A Stock in 2")
        deletepart(factoryidentity, typedata="stock", name="Machine A Stock out 1")


        json = createProduct(factoryidentity, "iPhone 10 RAWPART", "iPhone 10 ABCDEF TOP")
        produit1 = json["_id"]
        json = createProduct(factoryidentity, "iPhone 10 RAWPART", "iPhone 10 ABCDEF Bottom")
        produit2 = json["_id"]
        json = createStock(factoryidentity, "Stock A", "out")
        stockAId = json["_id"]
        json = createStock(factoryidentity, "Stock B", "in")
        stockBId = json["_id"]
        json = createStock(factoryidentity, "Machine A Stock in 1", "out") # stockin machine est un stock in robot
        stockMachineAin1 = json["_id"]
        json = createStock(factoryidentity, "Machine A Stock in 2", "out") # stockin machine est un stock in robot
        stockMachineAin2 = json["_id"]
        json = createStock(factoryidentity, "Machine A Stock out", "in") # stockout machine est un stock in robot
        stockMachineAout = json["_id"]

        json = createTaskMoveProductXFromStockAToStockB(factoryidentity, "Move Task 1", produit1, stockAId, stockMachineAin1)
        taskid1 = json["_id"]
        json = createTaskMoveProductXFromStockAToStockB(factoryidentity, "Move Task 2", produit2, stockAId, stockMachineAin2)
        taskid2 = json["_id"]
        json = createTaskMoveProductXFromStockAToStockB(factoryidentity, "Move Task 3", produit2, stockMachineAout, stockBId)
        taskid3 = json["_id"]

        newjob = defineNewJob(factoryidentity, "iPhone 10", [taskid1, taskid2, taskid3])

        job1 = createJob(factoryidentity, "Ma référence", "iPhone 10")
        job2 = createJob(factoryidentity, "Ma référence", "iPhone 154")

    agentJobToTask = AgentJobToTaskClass(1, "JobToTask", factoryidentity)


    agentJobToTask.start()
    print("done")
    agentJobToTask.join()
    print("end")

    # lock = thread.allocate_lock()
    # thread.start_new_thread(myfunction, ("Thread #: 1", 2, lock))
    # thread.start_new_thread(myfunction, ("Thread #: 2", 2, lock))
