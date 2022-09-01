from AgentThreaded import Regeneration
import sys
import time
import threading
# import requests
import pymongo


# verifier plus tard avec watch https://www.mongodb.com/blog/post/mongodb-change-streams-with-python
# https://api.mongodb.com/python/current/api/pymongo/change_stream.html
# https://www.tutorialspoint.com/python_design_patterns/python_design_patterns_observer.htm
# sys.path.append("..\\Commandes")
# from OrderAgentThreaded import AgentOrderToDoClass, AgentOrderToDoingClass, AgentOrderToDoneClass
# from JobAgentThreaded import AgentJobToTaskClass
import commandes.commandeAPI as commandeAPI
#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")


if __name__ == "__main__":
    # Connction base
    connection = pymongo.MongoClient('robigdata.rorecherche', 27017)
    database = connection.FOF
    Regeneration = True
    # database.list_collection_names()
    # ordre = database.order
    # coll = db.operation
    # factid = db.factory.find_one({'name':'Factory Vu Hoi'})['_id']
    # coll.find_one({"operationStatus":"done","operationType":"robotmove","factoryInfo":factid})

    factoryId = commandeAPI.findfactory(name="Factory LINEACT Test Fabrice")[0]
    if Regeneration:
        commandeAPI.deletepart(factoryId, typedata="job")
        commandeAPI.deletepart(factoryId, typedata="order")
        ordre1 = commandeAPI.createOrder(factoryId, "Ma référence", "iPhone 10 ", 5)

    agentOrderToDo = commandeAPI.AgentOrderToDoClass(1, "OrderToDo", factoryId)
    agentOrderToDoing = commandeAPI.AgentOrderToDoingClass(2, "OrderToDoing", factoryId)
    agentOrderToDone = commandeAPI.AgentOrderToDoneClass(3, "OrderToDone", factoryId)
    agentJobToTask = commandeAPI.AgentJobToTaskClass(1, "JobToTask", factoryId)


    agentOrderToDo.start()
    agentOrderToDoing.start()
    agentOrderToDone.start()
    agentJobToTask.start()
    print("Launched")
    try:
        while agentOrderToDo.is_alive() and agentOrderToDoing.is_alive() and agentOrderToDone.is_alive() and agentJobToTask.is_alive():
            time.sleep(10)
            print(".",end="")
    except KeyboardInterrupt:
        print("Keyboard Stop")
        agentOrderToDo.stop()
        agentOrderToDoing.stop()
        agentOrderToDone.stop()
        agentJobToTask.stop()
        print("all stop")
    




    # lock = thread.allocate_lock()
    # thread.start_new_thread(myfunction, ("Thread #: 1", 2, lock))
    # thread.start_new_thread(myfunction, ("Thread #: 2", 2, lock))
