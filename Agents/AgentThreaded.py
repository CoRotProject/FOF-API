import sys
import time
# import threading
# import requests
# import pymongo


# verifier plus tard avec watch https://www.mongodb.com/blog/post/mongodb-change-streams-with-python
# https://api.mongodb.com/python/current/api/pymongo/change_stream.html
# https://www.tutorialspoint.com/python_design_patterns/python_design_patterns_observer.htm
# sys.path.append("..\\Commandes")
from OrderAgentThreaded import AgentOrderToDoClass, AgentOrderToDoingClass, AgentOrderToDoneClass
from JobAgentThreaded import AgentJobToTaskClass
sys.path.append("..\\Commandes")
import commandes.commandeAPI as commandeAPI


if __name__ == "__main__":
    Regeneration = False
    factoryId = commandeAPI.findfactory(name="Factory LINEACT Test Fabrice")[0]
    if Regeneration:
        commandeAPI.deletepart(factoryId, typedata="job")
        commandeAPI.deletepart(factoryId, typedata="order")
        ordre1 = commandeAPI.createOrder(factoryId, "Ma référence", "iPhone 10 ", 5)

    agentOrderToDo = AgentOrderToDoClass(1, "OrderToDo", factoryId)
    agentOrderToDoing = AgentOrderToDoingClass(2, "OrderToDoing", factoryId)
    agentOrderToDone = AgentOrderToDoneClass(3, "OrderToDone", factoryId)
    agentJobToTask = AgentJobToTaskClass(1, "JobToTask", factoryId)


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
