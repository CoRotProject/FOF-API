# coding: utf8
# Copyright 2021 Fabrice DUVAL
# import requests
# import os
import sys
# import math
import time
# import random
import commandeAPI
import Agents.schedulerconnector as connector

#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

# global positions :
positions = {
    "poste1":{"x":36.25, "y":2.09, "theta":138.4, },
    "poste2":{"x":33.00, "y":-2.40, "theta":135.1, },
    "poste3":{"x":16.44, "y":-5.0, "theta":180.0, },
    "poste4":{"x":15.00, "y":3.50, "theta":6.29, },
    "input":{"x":3.31, "y":-3.43, "theta":0.11, },
    "output":{"x":43.19, "y":23.15, "theta":-91.35, },
    # "output":{"x":40.66, "y":5.90, "theta":30.44, },
}

def getposte(factoryid, nomposte):
    retour = {}
    retour["poste"] = commandeAPI.findINfactory(factoryid, "machine", name=nomposte)[0]
    retour["in"] = commandeAPI.findINfactory(factoryid, "stock", name=nomposte+" in")[0]
    retour["out"] = commandeAPI.findINfactory(factoryid, "stock", name=nomposte+" out")[0]
    return retour

if __name__ == "__main__":
    Regeneration = True
    NettoyageOnly = False
    print(commandeAPI.urlTemplate)
    print(commandeAPI.urlTemplateFactory)
    nomfact = "Factory LINEACT Mario"
    factoryid = commandeAPI.findfactory(name=nomfact)[0]
    if Regeneration:
        commandeAPI.deletepart(factoryid,typedata="operation")                          # database operation

    machine_position_indices, agvs_transportation_times_matrix = connector.getmachines(factoryid)
    process_plan = [{"j1" :connector.getprocessplan(factoryid,"job 1","O1")},
                    {"j2" :connector.getprocessplan(factoryid,"job 2","O2")},
                    {"j3" :connector.getprocessplan(factoryid,"job 3","O3")},
                    {"j4" :connector.getprocessplan(factoryid,"job 4","O4")},
                    {"j5" :connector.getprocessplan(factoryid,"job 5","O5")},]

    print("done")
