# Copyright 2021 Fabrice DUVAL

import time
# import imp
import sys
import queue
# import mir
import OperationAgent
import Agentproduce_CNC as machine
import CNC
import Commandes.commandeAPI as commandeAPI
#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

nomfactory = "Factory CERI"
nommachine = "CERI_CNC"
try:
    print("Machine in real: ",sys.argv[2])
    simulate = sys.argv[2].lower() != "real"
except IndexError:
    print("Machine simulated")
    simulate = True



try:
    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
except IndexError:
    print("Base inacessible. Pause puis quitte")
    time.sleep(10)
    exit("Base non valide")

try:
    machinebase = commandeAPI.findINfactory(factoryid, "machine", name=nommachine)[0]
except IndexError:
    print("machine {} inacessible. Pause puis quitte".format(nommachine))
    time.sleep(10)
    exit("machine non valide")


def testoperation():
    print("test operations")
    # factoryid = commandeAPI.findfactory(name=nomfactory)[0]
    # machineid = commandeAPI.findINfactory(factoryid, "machine", name=nommachine)[0]
    # machine = commandeAPI.getvalues(factoryid, "machine", machineid)
    # stockid = machine["stockList"][0]
    # stock = commandeAPI.getvalues(factoryid, "stock", stockid)
    # productid = commandeAPI.createProduct(factoryid, "Raw_Part N_1", "Raw_Par")["_id"]
    # if stock["mode"] == "internal":
    #     stockinterneid = stockid
    #     stockinterne = stock
    #     stockinoutid = machine["stockList"][1]
    #     stockinout = commandeAPI.getvalues(factoryid, "stock", stockinoutid)
    # else:
    #     stockinoutid = stockid
    #     stockinout = stock
    #     stockinterneid = machine["stockList"][1]
    #     stockinterne = commandeAPI.getvalues(factoryid, "stock", stockinterneid)

    # commandeAPI.updateobject(factoryid, "product", productid, {"link":stockinoutid})

if __name__ == "__main__":
    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
    deleteope = True
    createope = False


    print("Launch Operation Agent " + nommachine + commandeAPI.urlTemplate)
    resource = commandeAPI.findINfactory(factoryid, "resource", name=nommachine)[0]
    if deleteope:
        commandeAPI.deletepart(factoryid, typedata="operation", resourceInfo=resource)
    if createope:
        testoperation()

    machinereel = CNC.CNC(nom=nommachine)

    # create communication FIFO
    fifoproduce = queue.Queue() # create FIFO of valide operation
    fiforetproduce = queue.Queue() # create FIFO of return value for database
    fifoop = {"production":fifoproduce,}
    fiforet = {"production":fiforetproduce,}

    opagent = OperationAgent.AgentOperation(1, nomfactory+" "+nommachine, factoryid, resource, nommachine, ["production"], fifoop, fiforet)
    # robot_agent = AgentProduce_CNC.AgentProduceCNC(nomfactory+" "+nommachine, factoryid, robotreel, fiforobotmove, fiforetrobotmove)
    machine_agent = machine.AgentProduceCNC(nomfactory+" "+nommachine, factoryid, resource, machinereel, fifoproduce, fiforetproduce, simumode = True)

    if simulate:
        cncsimulator = CNC.CNCSimulate()
        cncsimulator.start()
    
    opagent.start()
    machine_agent.start()
    print("done")
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        opagent.terminate()
        machine_agent.terminate()
        if simulate:
            cncsimulator.terminate()

    print("killed")