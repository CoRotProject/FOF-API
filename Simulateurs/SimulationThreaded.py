import requests
import sys
import pymongo
import time
import threading
from SimuRobotThreaded import RobotMir
import Commandes.commandeAPI as commandeAPI
#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

if __name__ == "__main__":
    Regeneration = False
    factoryid = commandeAPI.findfactory(name="Factory LINEACT simulated")[0]
    agents = []

    #robots
    mir100ArmId = commandeAPI.findINfactory(factoryid, "resource", name="mir100_Arm")[0]
    mir100CapitaineId = commandeAPI.findINfactory(factoryid, "resource", name="mir100_Capitaine")[0]

    agents.append(RobotMir(1,factoryid, mir100ArmId, vitesse=10, temps=1))
    agents.append(RobotMir(1,factoryid, mir100CapitaineId, vitesse=10, temps=1))

    # agentOrderToDo = agentTestOrderToDoClass(1, "OrderToDo", factoryId)
    # agentOrderToDoing = agentTestOrderToDoingClass(2, "OrderToDoing", factoryId)
    # agentOrderToDone  = agentTestOrderToDoneClass(3, "OrderToDone", factoryId)
    # agentJobToTask = agentTestJobToTaskClass(1, "JobToTask", factoryId)


    # agentOrderToDo.start()
    # agentOrderToDoing.start()
    # agentOrderToDone.start()
    # agentJobToTask.start()

    #all run
    for agent in agents:
        agent.start()



    print("done")
    try:
        while(True):
            time.sleep(1)
    except KeyboardInterrupt:
        for agent in agents:
            agent.terminate()
    print("killed")

