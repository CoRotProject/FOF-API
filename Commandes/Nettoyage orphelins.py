import sys
import commandeAPI
from pymongo import MongoClient
from bson.objectid import ObjectId

#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

try:
    print("DB in remote mode: ",sys.argv[2])
    client = MongoClient(sys.argv[2])
except IndexError:
    print("DB in local 127.0.0.1")

def cleandatabase(listefactoryok, document):
    total = 0
    liste=document.find()
    for element in liste:
        print(element["_id"],end="")
        print(" ==> ",end="")
        if element["factoryInfo"] not in listefactoryok:
            document.delete_one({'_id':element['_id']})
            print("détruit")
            total += 1
    return total



if __name__ == "__main__":
    ListeCorrectsFactory = ["Factory LINEACT Real", "Factory LINEACT Virtual", "Factory CERI",
            "Factory LINEACT Mario", "Factory Said", "TEST", "PIP TEST Real", "TURTLEBOTS ARENA", "smart factory lab lineact",]
    print(commandeAPI.urlTemplate)
    print(commandeAPI.urlTemplateFactory)
    listfactoryid = []
    for factory in ListeCorrectsFactory:
        # recup valid ID
        listeinbase = commandeAPI.findfactory(name=factory)
        if listeinbase:
            listfactoryid.extend(listeinbase)
    factoryobjectid = []
    for factoryid in listfactoryid:
        factoryobjectid.append(ObjectId(factoryid))

    
    print("purge !")
    db=client.FOF
    liste=db.operation.find()
    nbjob = cleandatabase(factoryobjectid, db.job)
    nbjobdescription = cleandatabase(factoryobjectid, db.jobdescription)
    nboperation = cleandatabase(factoryobjectid, db.operation)
    nborder = cleandatabase(factoryobjectid, db.order)
    nbproduct = cleandatabase(factoryobjectid, db.product)
    nbresource = cleandatabase(factoryobjectid, db.resource)
    nbstock = cleandatabase(factoryobjectid, db.stock)
    nbtask = cleandatabase(factoryobjectid, db.task)
    print([nbjob, nbjobdescription, nboperation, nborder, nbproduct, nbresource, nbstock, nbtask])
