import sys
import commandes.commandeAPI as commandeAPI

from OrderAgentThreaded import AgentOrderToDoClass, AgentOrderToDoneClass, AgentOrderToDoneClass

debug = True

if __name__ == "__main__":
    if debug:
        factoryId = commandeAPI.findfactory(name="Factory LINEACT Test Fabrice")[0]


    agentOrderToDo = commandeAPI.AgentTestOrderToDoClass(1, "OrderToDo", factoryId)
    agentOrderToDoing = commandeAPI.AgentTestOrderToDoingClass(2, "OrderToDoing", factoryId)
    agentOrderToDone = commandeAPI.AgentTestOrderToDoneClass(3, "OrderToDone", factoryId)
    agentJobToTask = commandeAPI.AgentTestJobToTaskClass(1, "JobToTask", factoryId)


    agentOrderToDo.start()
    agentOrderToDoing.start()
    agentOrderToDone.start()
    agentJobToTask.start()