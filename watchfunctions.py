from flask import request, Response
import time
import Commandes.commandeAPI as commandeAPI
from xml.dom import minidom as dom
import pymongo

mongodburl = commandeAPI.urlTemplate.split('://')[-1].split(':')[0]
mongodbport = 27017
watchtimeout = 60


def evalstr(chaine):
    if chaine[0]==chaine[-1] and (chaine[0]=="'" or chaine[0]=='"'):
        return chaine[1:-1]
    elif chaine.upper == 'TRUE':
        return True
    elif chaine.upper == 'FALSE':
        return False
    else:
        try:
            return int(chaine)
        except ValueError:
            try:
                return float(chaine)
            except ValueError:
                return chaine

def isitok(object, question):
    return "$match"


def anyreq(factoryid, objecttype, objectid, question):
    root = dom.Document()
    xml = root.createElement('watch')
    root.appendChild(xml)
    timein = root.createElement('request_time')
    xml.appendChild(timein)
    text = root.createTextNode(str(time.time()))
    timein.appendChild(text)
    objets = commandeAPI.getvalues(factoryid, objecttype, objectid)
    if objets == "None":
        text = root.createTextNode('error')
        xml.appendChild(text)
        timeout = root.createElement('return_time')
        xml.appendChild(timeout)
        text = root.createTextNode(str(time.time()))
        timeout.appendChild(text)
        return Response(root.toprettyxml(indent="  "), mimetype='text/xml')
    #watched object exist !


    clientmongo = pymongo.MongoClient(mongodburl,mongodbport)
    database = clientmongo['FOF']
    collection = database[objecttype]
    pipeline = [{'$match': {'_id': objectid}},]
    resume_token = None
    watchok = False
    while watchok:
        try:
            resume_token = None
            with collection.watch(pipeline=pipeline, resume_after=resume_token) as stream:
                for change in stream:
                    print(change)
                    resume_token = stream.resume_token
        except pymongo.errors.PyMongoError:
            # The ChangeStream encountered an unrecoverable error or the
            # resume attempt failed to recreate the cursor.
            if resume_token is None:
                # There is no usable resume token because there was a
                # failure during ChangeStream initialization.
                print("erreur de connexion")
            else:
                continue

    time.sleep(0.10)
    print("out")
    # return "factoryid=" + factoryid + ' ' + objecttype +'id=' + objectid + " result=" + retour +'\n' + question
    return Response(root.toprettyxml(indent="  "), mimetype='text/xml')
    # return None


def operation(factoryid=None, opidentity=None):
    # question = ""
    # for key, val in request.args.items():
    #     question = question + "key = " + key + " ; valeur = " + val + "\n"

    return anyreq(factoryid, "operation", opidentity, dict(request.args.items()))


def task(factoryid=None, tidentity=None):
    # question = ""
    # for key, val in request.args.items():
    #     question = question + "key = " + key + " ; valeur = " + val + "\n"

    return anyreq(factoryid, "task", tidentity, dict(request.args.items()))

def none():
    return ' Pouette'
