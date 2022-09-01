# coding: utf8
# Copyright 2020 Fabrice DUVAL
# import requests
# import random
import sys
from pyquaternion import Quaternion
import commandeAPI

#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

NomFactory = "Factory Test Map"


if __name__ == "__main__":
    Regeneration = True
    NewFactoryId = True
    print(commandeAPI.urlTemplate)
    print(commandeAPI.urlTemplateFactory)
    if Regeneration:
        # etape affacement de l'ancienne base
        listeinbase = commandeAPI.findfactory(name=NomFactory)
        effaceFactory = (len(listeinbase) != 1)  or NewFactoryId
        for usine in listeinbase:
            if effaceFactory:
                commandeAPI.deletepart(usine)
        if effaceFactory:
            json = commandeAPI.createFactory(NomFactory)
            factoryId = json["_id"]
        else:
            factoryId = usine
    else:
        factoryId = commandeAPI.findfactory(name=NomFactory)[0]
    commandeAPI.mapinfactory(factoryId, "..\\Visualisation\\Madrillet.png", (1, 2, 45), 0.05)
    print("done")
