import sys
# import requests
# import pymongo
import time
import threading
import commandes.commandeAPI as commandeAPI
#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

# database= pymongo.MongoClient('mongodb://192.168.1.21:27017/')
# fof=database.FOF
# # fof.list_collection_names()
# factory=fof.factory
# order=database.order
# MyFactory = factory.find_one({'name':'Factory LINEACT Test Fabrice'})["_id"]

# from bson.objectid import ObjectId
# only if post_id is a string instead of objectid
# # The web framework gets post_id from the URL and passes it as a string
# def get(post_id):
#     # Convert from string to ObjectId:
#     document = client.db.collection.find_one({'_id': ObjectId(post_id)})

exitFlag = 0

class AgentOrderToDoClass(threading.Thread):
    """teste les ordres "todo" (a valider)"""
    def __init__(self, threadID, name, factoryId):
        threading.Thread.__init__(self)
        self.threadid = threadID
        self.name = name
        self.factoryid = factoryId
        self._running = True
    def run(self):
        while self._running:
            finded_unseen_order = commandeAPI.findINfactory(self.factoryid, "order", orderStatus="toDo")
            # if len(FindedUnseenOrder)>0:
            for achanger in finded_unseen_order:
                # achanger = FindedUnseenOrder[0]
                commandeAPI.updatestatus(self.factoryid, "order", achanger, "toDoAcknowledge")
                ordrebase = commandeAPI.getvalues(self.factoryid, "order", achanger)
                listejob = []
                for aaaa in range(ordrebase["quantity"]):
                    listejob.append(commandeAPI.createJob(self.factoryid, ordrebase["name"]+"_{:06}".format(aaaa+1), ordrebase["productToDo"])["_id"])
                commandeAPI.updateobject(self.factoryid, "order", achanger, {"jobList": listejob})
                commandeAPI.updatestatus(self.factoryid, "order", achanger, "toDoSplitedIntoJobs")
            time.sleep(1)
    def stop(self):
        self._running = False

class AgentOrderToDoingClass(threading.Thread):
    """teste les ordres "todoing" (a valider)"""
    def __init__(self, threadID, name, factoryId):
        threading.Thread.__init__(self)
        self.threadid = threadID
        self.name = name
        self.factoryid = factoryId
        self._running = True
    def run(self):
        while self._running:
            finded_unseen_order = commandeAPI.findINfactory(self.factoryid, "order", orderStatus="toDoSplitedIntoJobs")
            for atester in finded_unseen_order:
                ordrebase = commandeAPI.getvalues(self.factoryid, "order", atester)
                jobdoing = False
                jobfalse = False
                for jobinlist in ordrebase["jobList"]:
                    jobtest = commandeAPI.getvalues(self.factoryid, "job", jobinlist)
                    if jobtest["jobStatus"] in ('toDoAcknowledge', 'doing', 'done'):
                        jobdoing = True
                    if jobtest["jobStatus"] == 'error':
                        jobfalse = True
                if jobfalse:
                    commandeAPI.updatestatus(self.factoryid, "order", atester, "error")
                elif jobdoing:
                    commandeAPI.updatestatus(self.factoryid, "order", atester, "doing")
            time.sleep(5)
    def stop(self):
        self._running = False

class AgentOrderToDoneClass(threading.Thread):
    """teste les ordres "todone" (a valider)"""
    def __init__(self, threadID, name, factoryId):
        threading.Thread.__init__(self)
        self.threadid = threadID
        self.name = name
        self.factoryid = factoryId
        self._running = True
    def run(self):
        while self._running:
            finded_unseen_order = commandeAPI.findINfactory(self.factoryid, "order", orderStatus="doing")
            for atester in finded_unseen_order:
                ordrebase = commandeAPI.getvalues(self.factoryid, "order", atester)
                jobdone = True
                jobfalse = False
                for jobinlist in ordrebase["jobList"]:
                    jobtest = commandeAPI.getvalues(self.factoryid, "job", jobinlist)
                    if jobtest["jobStatus"] != 'done':
                        jobdone = False
                    if jobtest["jobStatus"] == 'error':
                        jobfalse = True
                if jobfalse:
                    commandeAPI.updatestatus(self.factoryid, "order", atester, "error")
                elif jobdone:
                    commandeAPI.updatestatus(self.factoryid, "order", atester, "done")
            time.sleep(5)
    def stop(self):
        self._running = False


if __name__ == "__main__":
    Regeneration = True
    factoryidentity = commandeAPI.findfactory(name="Factory LINEACT Test Fabrice")[0]
    if Regeneration:
        commandeAPI.deletepart(factoryidentity, typedata="job")
        commandeAPI.deletepart(factoryidentity, typedata="order")
        ordre1 = commandeAPI.createOrder(factoryidentity, "Ma référence", "Yolo", 5)

    agentOrderToDo = AgentOrderToDoClass(1, "OrderToDo", factoryidentity)
    agentOrderToDoing = AgentOrderToDoneClass(2, "OrderToDoing", factoryidentity)
    agentOrderToDone = AgentOrderToDoneClass(3, "OrderToDone", factoryidentity)

    agentOrderToDo.start()
    agentOrderToDoing.start()
    agentOrderToDone.start()
    print("done")

    # lock = thread.allocate_lock()
    # thread.start_new_thread(myfunction, ("Thread #: 1", 2, lock))
    # thread.start_new_thread(myfunction, ("Thread #: 2", 2, lock))
