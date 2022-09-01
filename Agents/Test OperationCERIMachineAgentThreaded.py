# Copyright 2021 Fabrice DUVAL

import time
import sys
import math
import Commandes.commandeAPI as commandeAPI

#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")
print("Test at CERI")

debugbaseenlocal = False
nomfactory = "Factory CERI"

if len(sys.argv) > 1 :
    nommachine = sys.argv[1]
else:
    nommachine = "Usinage_CERI"

if debugbaseenlocal:
    commandeAPI.urlTemplateFactory = commandeAPI.urlTemplateFactory.replace('robigdata.rorecherche', '127.0.0.1')
    commandeAPI.urlTemplate = commandeAPI.urlTemplate.replace('robigdata.rorecherche', '127.0.0.1')

try:
    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
except IndexError:
    print("Base inacessible. Pause puis quitte")
    time.sleep(10)
    exit("Base non valide")

try:
    machinebase = commandeAPI.findINfactory(factoryid,"machine", name=nommachine)[0]
except IndexError:
    print("machine {} inacessible. Pause puis quitte".format(nommachine))
    time.sleep(10)
    exit("Robot non valide")

def dist(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2+(y1-y2)**2)

if __name__ == "__main__":
    Regenerationope = True
    print("Launch Machine Agent " + nommachine + " connected to database " + commandeAPI.urlTemplate)
    if Regenerationope:
        commandeAPI.deletepart(factoryid, typedata="operation", resourceInfo=machinebase)

    operation1 = commandeAPI.createOperationMachine(factoryid, machinebase, name="Usinage")["_id"] # vertical
    operation2 = commandeAPI.createOperationMachine(factoryid, machinebase, name="Usinage", previous=operation1)["_id"] # vertical
    operation3 = commandeAPI.createOperationMachine(factoryid, machinebase, name="Usinage", previous=operation2)["_id"] # vertical
    # operation3 = commandeAPI.createOperationMoveRobotTo(factoryid, robotbase, (0.0, 0.0, 90.0, poste1["in"]))["_id"] # vertical

    commandeAPI.updatestatus(factoryid, "operation", operation1, "toDo")
    commandeAPI.updatestatus(factoryid, "operation", operation2, "toDo")
    commandeAPI.updatestatus(factoryid, "operation", operation3, "toDo")

    print("end")
