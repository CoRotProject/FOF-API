# coding: utf8
# Copyright 2021 Fabrice DUVAL
# import requests
# import os
import sys
import math
# import time
# import random
# from pyquaternion import Quaternion
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
    nomfactory = "Factory LINEACT Mario"

factoryid = commandeAPI.findfactory(name=nomfactory)[0]

def getmachines(factoryid, agvmeanspead=1.0):
    stocklist = commandeAPI.findINfactory(factoryid,"stock")
    machinelist = commandeAPI.findINfactory(factoryid,"machine")
    positionsparams={}
    for stock in stocklist:
        # wmachine = commandeAPI.getvalues(factoryid, "machine", machine)
        wstock = commandeAPI.getvalues(factoryid, "stock", stock)
        if "link" not in wstock:
            positionsparams[wstock["name"]] = wstock["transform2D"]
    for machine in machinelist:
        wmachine = commandeAPI.getvalues(factoryid, "machine", machine)
        positionsparams[wmachine["name"]] = commandeAPI.findrealposition(factoryid, wmachine)
    
    positionindex = dict(zip(positionsparams.keys(), range(len(positionsparams))))
    temps={}
    for nameF, positionF in positionsparams.items():
        temps[nameF] = {}
        for nameT, positionT in positionsparams.items():
            deltax = positionT["x"] - positionF["x"]
            deltay = positionT["y"] - positionF["y"]
            deltatheta = positionT["theta"] - positionF["theta"]
            temps[nameF][nameT] = (math.sqrt(deltax * deltax + deltay * deltay) + abs(deltatheta) / 90) / agvmeanspead

    return positionindex, temps

def getprocessplan(factoryid, jobname, beginoperationname="O1"):
    try:
        findjobprototype = commandeAPI.findINfactory(factoryid, "jobdescription", name=jobname)[0] #only first taking into account
    except IndexError:
        return None
    
    returnvalue={}

    machinelist = commandeAPI.findINfactory(factoryid,"machine")
    fulllistcapabilities={}
    for machine in machinelist:
        currentmachine = commandeAPI.getvalues(factoryid, "machine", machine)
        for capability in currentmachine['resourceCapabilityList']:
            if capability["capability"] in fulllistcapabilities:
                fulllistcapabilities[capability["capability"]].append([currentmachine["name"], capability["duration"],])
            else:
                fulllistcapabilities[capability["capability"]] = [[currentmachine["name"], capability["duration"],],]


    jobdescription = commandeAPI.getvalues(factoryid, "jobdescription", findjobprototype) #only first taking into account
    for liste, tasktodo in enumerate(jobdescription["taskList"]):
        returnvalue[beginoperationname+str(liste+1)]=[]
        taskvalue = commandeAPI.getvalues(factoryid, "taskProduce", tasktodo)
        for machine in fulllistcapabilities[taskvalue["taskName"]]:
            returnvalue[beginoperationname+str(liste+1)].append({"machine_id":machine[0], "operation_type_id":taskvalue["taskName"], "processing_time":machine[1]})

    return returnvalue


if __name__ == "__main__":
    machine_position_indices, agvs_transportation_times_matrix = getmachines(factoryid)
    process_plan = [{"j1" :getprocessplan(factoryid,"job 1","O1")},
                    {"j2" :getprocessplan(factoryid,"job 2","O2")},
                    {"j3" :getprocessplan(factoryid,"job 3","O3")},
                    {"j4" :getprocessplan(factoryid,"job 4","O4")},
                    {"j5" :getprocessplan(factoryid,"job 5","O5")},]
    print("done")
