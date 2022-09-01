# coding: utf8
# Copyright 2020 Fabrice DUVAL
# import socket
import os
import random
import math
import base64
import requests
import io
import time
from PIL import Image
# from pyquaternion import Quaternion
# from bson.dbref import DBRef
# from bson import json_util

# version mise à jour Suppression totale de la detection du serveur

urlTemplate = ''
urlTemplateFactory = ''

def seturl(ip):
    global urlTemplate
    global urlTemplateFactory
    urlTemplate = ip
    urlTemplateFactory = urlTemplate+'factory/{factoryid}/'

def check_ping(hostname):
    """test d'existance de hostname"""
    if os.name == 'nt':
        return (os.system("ping -n 1 -w 300 " + hostname + " >nul") == 0)
    else:
        return (os.system("ping -c 1 -w 1 " + hostname + " >/dev/null") == 0)

def findfactory(**condition):
    """
    find ID of factory with condition
    condition = {"name"="Factory"}
    example = findfactory("name"="Factory LINEACT Test")
    return the IDs of the factory
    """
    url = urlTemplate+'factory'
    if condition:
        url += '?where={'
        for num, item in enumerate(condition.items()):
            if num > 0:
                url += '&'
            url += '\"' + item[0] + '\": '+'\"'+item[1]+'\"'
        url += '}'
    response = requests.get(url)

    if response.status_code == 200 or response.status_code == 201:
        jsonResponse = response.json()
        liste = []
        for reslt in jsonResponse['_items']:
            liste.append(reslt['_id'])
        return liste

    return None

def findINfactory(factoryid, typedata, **condition):
    """
    find ID of object with condition
    condition = {"name"="Factory"}
    example = findfactory("name"="Factory LINEACT Test")
    return the IDs of the factory
    """
    url = urlTemplateFactory.replace('{factoryid}', factoryid) + typedata+"/"
    if condition:
        url += '?where={'
        for num, item in enumerate(condition.items()):
            if num > 0:
                url += ','
            if item[1] == None or item[1] == 'null':
                url += '\"' + item[0] + '\": '+ 'null'
            else:
                url += '\"' + item[0] + '\": '+'\"'+item[1]+'\"'
        url += '}'
    response = requests.get(url)
    
    if response.status_code == 200 or response.status_code == 201:
        jsonResponse = response.json()
        liste = []
        for reslt in jsonResponse['_items']:
            liste.append(reslt['_id'])
        return liste

    return None

def deletepart(factoryid, typedata=None, iddata=None, **findit):
    """typedata (operation, robot...)
    iddata = list of id
    findit = conditions (if exist, destroy iddata)"""
    url = urlTemplateFactory.replace('{factoryid}', factoryid) 
    if typedata:
        url += typedata + "/"
        if findit:
            iddata = findINfactory(factoryid,typedata,**findit)
            if not iddata:
                return 0
        if iddata:
            valretour = []
            nb = 0
            for valeur in iddata:
                nb += 1
                urltemp = url + valeur +"/"
                valretour.append(requests.delete(urltemp).status_code)
            if nb:
                return valretour[0]
            else:
                return valretour

        else:
            return requests.delete(url).status_code
    else:
        # Usine destroy !!
        return requests.delete(url).status_code

def createFactory(name):
    """
    create a factory with name
    return the id of the factory
    """
    url = urlTemplate+'factory'
    data = {"name": name}
    response = requests.post(url, json=data)

    return response.json()

def getMap(factoryid, path, name):
    """Récupération de la carte de la factoryid
    sayvegarde dans path de name.png et de name.yaml
    """
    carte = getfactory(factoryid)
    #image de la map
    imageFactoryPNG = base64.b64decode(carte["plan"]["picture"].encode("utf-8"))
    image = Image.open(io.BytesIO(imageFactoryPNG))
    image.save(path+name+".png", "PNG")
    #params de la map
    ox = carte["plan"]["offset"]["x"]
    oy = carte["plan"]["offset"]["y"]
    oscale =  carte["plan"]["scale"]
    params = "image: "+name+".png\nresolution: "+str(oscale)+"\norigin: ["+str(ox)+", "+str(oy)+", 0.000000]\nnegate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.196"
    fichierYaml = open(path+name+".yaml", "w")
    fichierYaml.write(params)
    fichierYaml.close()

def mapinfactory(factoryid, carte, offset=None, scale=None):
    """carte = Nom du fichier
    offset decalage en x,y, theta (non prise en compte de theta)
    scale en m par pixel"""
    url = urlTemplateFactory.replace('{factoryid}', factoryid)
    if carte:
        if not offset:
            offset = (0, 0, 0)
        if not scale:
            scale = 1
        with open(carte.replace("\\","/"), "rb") as file:
            image = bytearray(file.read())
        imageb64 = base64.b64encode(image)
        data = {
            "plan":{
                "picture": imageb64.decode("utf-8"),
                "offset": {"x":offset[0], "y":offset[1], "theta":offset[2]},
                "scale": scale,
            }
        }
        response = requests.patch(url, json=data)

        if response.status_code == 200 or response.status_code == 201:
            return True

    return False

def takereservation(factoryid, takeresourceid,forresourceid):
    """take takeresourceid for reservation for forresourceid
    return True if reservation ok false otherwise"""
    sourcestatus = getstatus(factoryid,"resource",takeresourceid)
    if not sourcestatus == "free":
        return False
    updateobject(factoryid, "resource", takeresourceid, {"status":"busy", "internalParams": {"reservedby": forresourceid},})
    time.sleep(1.0)
    sourcevalue = getvalues(factoryid,"resource",takeresourceid)
    if sourcevalue["internalParams"]["reservedby"] == forresourceid:
        return True
    else:
        return False

def releasereservation(factoryid, takeresourceid,forresourceid):
    """release takeresourceid for reservation for forresourceid
    return True if reservation is release from correct resource false otherwise"""
    sourcevalue = getvalues(factoryid,"resource",takeresourceid)

    if not sourcevalue["status"] == "busy":
        return False
    if sourcevalue["internalParams"]["reservedby"] == forresourceid:
        updateobject(factoryid, "resource", takeresourceid, {"status":"free", "internalParams": {"reservedby": ""},})
        return True
    else:
        return False

def createMiscResource(factoryid, name, position2d=None, link=None):
    """
    create a robot with name
    return the id of the factory
    """
    url = urlTemplateFactory.replace('{factoryid}', factoryid)+'resource'
    data = {
        "name": name,
        "resourceType": "misc",
        "status": "free",
        "transform2D": { 
                "x": 0, "y": 0, "theta": 0
        },
        "resourceCapabilityList": [{"category": "resourceunique"},],
        "internalParams": {"reservedby":""},
    }
    if position2d:
        data["transform2D"] = position2d
    if link:
        data["link"] = link
    response = requests.post(url, json=data)

    return response.json()

def createRobotResource(factoryid, name, robotType, resourceCapabilityList, position2d=None, link=None):
    """
    create a robot with name
    return the id of the factory
    """
    url = urlTemplateFactory.replace('{factoryid}', factoryid)+'robot'
    data = {
        "name": name,
        "resourceType": "robot",
        "robotType": robotType,
        "transform2D": { 
                "x": 0, "y": 0, "theta": 0
        },
        "resourceCapabilityList": resourceCapabilityList
    }
    if position2d:
        data["transform2D"] = position2d
    if link:
        data["link"] = link
    response = requests.post(url, json=data)

    return response.json()

def createHumanResource(factoryid, name, role, resourceCapabilityList):
    """
    create a robot with name
    return the id of the factory
    """
    url = urlTemplateFactory.replace('{factoryid}', factoryid)+'human'
    data = {
        "name": name,
        "resourceType": "human",
        'role': role,
        "transform2D": { 
                "x": 0, "y": 0, "theta": 0
        },
        "resourceCapabilityList": resourceCapabilityList
    }
    response = requests.post(url, json=data)
    return response.json()

def createMetaResource(factoryid, name, metaType, composition):
    """
    create a robot with name
    return the id of the factory
    """
    url = urlTemplateFactory.replace('{factoryid}', factoryid)+'meta'
    data = {
        "name": name,
        "resourceType": "meta",
        "metaType": metaType,
        "composition" : composition,
    }
    response = requests.post(url, json=data)

    return response.json()

def createOrder(factoryid, reference, producttodo, nombre):
    """
    create an order "reference" with a product name and quantity
    return the id of the factory
    """
    url = urlTemplateFactory.replace('{factoryid}', factoryid)+'order'
    data = {
        "name": reference,
        "productToDo": producttodo,
        'quantity': nombre,
        'orderStatus': 'toDo',
    }
    response = requests.post(url, json=data)
    return response.json()

def createJob(factoryid, reference, producttodo):
    """
    create an order "reference" with a product name and quantity
    return the id of the factory
    """
    url = urlTemplateFactory.replace('{factoryid}', factoryid)+'job'
    data = {
        "name": reference,
        "productToDo": producttodo,
        'jobStatus': 'toDo',
    }
    response = requests.post(url, json=data)
    return response.json()

def updateRobotPoseRandom(factoryid, robotId): #à modifier ==>2D
    """
    Update the robot position with Vector3 and Quaternion
    """

    url = urlTemplateFactory.replace('{factoryid}', factoryid)+'robot/'+robotId
    data = {
        "transform2D": { 
            "x": random.uniform(0, 10) , 
            "y":  random.uniform(0, 10),
            "theta":  random.uniform(-180, 180),
        }
    }
    response = requests.patch(url, json=data)

    if response.status_code == 200 or response.status_code == 201 :
        return True

    return False

def updatestatus(factoryid, typedocument, ident, status):
    url = urlTemplateFactory.replace('{factoryid}', factoryid)+typedocument+'/'+ident
    data = {
        "status": status
    }
    response = requests.patch(url, json=data)

    if response.status_code == 200 or response.status_code == 201 :
        return True

    return False

def updateobject(factoryid, objecttype, objectid, data):
    url = urlTemplateFactory.replace('{factoryid}', factoryid)+objecttype+'/'+objectid

    response = requests.patch(url, json=data)

    if response.status_code == 200 or response.status_code == 201 :
        return True

    return False

def testoperation(factoryid, operationid):
    # url = urlTemplateFactory.replace('{factoryid}', factoryid)+'operation/'+operationid
    # response = requests.get(url)
    # if response.status_code in (200,201,202):
    #     return response.json()["operationStatus"]
    # else:
    #     return 'None'
    return getvalues(factoryid, "operation", operationid)["status"]

def getvalues(factoryid, objecttype, ident):
    url = urlTemplateFactory.replace('{factoryid}', factoryid)+objecttype+'/'+ident
    response = requests.get(url)
    if response.status_code in (200, 201, 202):
        return response.json()
    else:
        return 'None'

def getstatus(factoryid, objecttype, ident):
    url = urlTemplateFactory.replace('{factoryid}', factoryid)+objecttype+'/'+ident
    response = requests.get(url)
    if response.status_code in (200, 201, 202):
        try:
            return response.json()['status']
        except KeyError:
            return None
        return response.json()
    else:
        return None

def getfactory(factoryid):
    url = urlTemplateFactory.replace('{factoryid}', factoryid)
    response = requests.get(url)
    if response.status_code in (200, 201, 202):
        return response.json()
    else:
        return 'None'

def createStock(factoryid, name, mode, position2d=None, position=None, link=None, typestock='stockPart', posarray=[1, 1], vectarray=[0.0, 0.0]):
    """
    Create a stock Product with random pos Vector3 and Quaternion
    return json response
    """

    url = urlTemplateFactory.replace('{factoryid}', factoryid)+'stock'
    if position is None:
        position = {
            "position":
                {
                    "x": 0.0 , "y":  0.0, "z":  0.0
                },
            "rotation":
                {
                    "qx":  0.0, "qy": 0.0, "qz": 0.0, "qw": 0.0	
                }
            }
    if position2d is None:
        position2d = {
            "x": 0.0 ,
            "y":  0.0,
            "theta": 0.0,
        }
    data = {
        "name":name,
        "transform": position,
        "transform2D": position2d,
        "mode":mode,
        "stockType":typestock,
        "size":{
            "nbx":posarray[0],
            "nby":posarray[1],
            "deltax":vectarray[0],
            "deltay":vectarray[0],
        },
    }
    if link:
        data["link"] = link
    response = requests.post(url, json=data)

    return response.json()

def createProduct(factoryid, name, reference):
    """
    Create a product in the factory
    return json response
    """

    url = urlTemplateFactory.replace('{factoryid}', factoryid)+'product'
    data = {
        "name":name,
        "reference": reference
    }
    response = requests.post(url, json=data)

    return response.json()

def createTaskMoveProductXFromStockAToStockB(factoryid, name, productId, stockAId, stockBId, resource=None, precedence=None):
    """
    Create a task for moving a product from stockA to stockB
    return json response
    """

    url = urlTemplateFactory.replace('{factoryid}', factoryid)+'taskMoveProductXFromStockAToStockB'
    data = {
        "name":name,
        # "taskType": "taskMoveProductXFromStockAToStockB",
        "productInfo":productId,
        "stockAInfo":stockAId,
        "stockBInfo":stockBId
    }
    if resource:
        data["resourceInfo"] = resource
    if precedence:
        data["precedenceTaskInfo"] = formalize2list(precedence)

    response = requests.post(url, json=data)

    return response.json()

def createTaskMoveProductXFromAToB(factoryid, name, productId, stockAId=None, Atxt=None, stockBId=None, Btxt=None, resource=None, precedence=None):
    """
    Create a task for moving a product from stockA to stockB
    return json response
    """

    url = urlTemplateFactory.replace('{factoryid}', factoryid)+'taskMoveProductXFromStockAToStockB'
    data = {
        "name":name,
        # "taskType": "taskMoveProductXFromAToB",
        "productInfo":productId,
    }
    if stockAId:
        data["stockAInfo"] = stockAId
    if Atxt:
        data["stockAInfoTxt"] = Atxt
    if stockBId:
        data["stockBInfo"] = stockBId
    if Btxt:
        data["stockBInfoTxt"] = Btxt
    if resource:
        data["resourceInfo"] = resource
    if precedence:
        data["precedenceTaskInfo"] = formalize2list(precedence)

    response = requests.post(url, json=data)

    return response.json()

def createTaskProduce(factoryid, name, taskname, outputname, listrawparts, listinputparts,resource=None, precedence=None):
    """
    Create a task for creating object 'outputname' from list of raw material and input part
    return json response
    """

    url = urlTemplateFactory.replace('{factoryid}', factoryid)+'taskProduce'
    data = {
        "name":name,
        "taskName":taskname, # if machine can produce in different way
        "endPartNames":outputname, # if naming is necessary
        "rawPartNames":formalize2list(listrawparts),
        "inputPartIds":formalize2list(listinputparts),
    }
    if resource:
        data["resourceInfo"] = resource
    if precedence:
        data["precedenceTaskInfo"] = formalize2list(precedence)

    response = requests.post(url, json=data)

    return response.json()

def createTaskHuman(factoryid, name, taskname, outputname, listrawparts, listinputparts, listtexttask, position=None, resource=None, precedence=None ):
    """
    Create a task for creating object 'outputname' from list of raw material and input part
    return json response
    """

    url = urlTemplateFactory.replace('{factoryid}', factoryid)+'taskHuman'
    data = {
        "name":name,
        "taskName":taskname, # if machine can produce in different way
        "endPartNames":outputname, # if naming is necessary
        "rawPartNames":formalize2list(listrawparts),
        "inputPartIds":formalize2list(listinputparts),
        "taskstodo":formalize2list(listtexttask),
    }
    if isinstance(position, list) or isinstance(position, tuple):
        data['transform2D'] =  {'x':position[0], 'y':position[1], 'theta':position[2],}
        if len(position)>3:
            data['stockInfo'] = position[3]
    if resource:
        data["resourceInfo"] = resource
    if precedence:
        data["precedenceTaskInfo"] = formalize2list(precedence)

    response = requests.post(url, json=data)

    return response.json()

def duplicatetask(factoryid, taskId, name, named=False): # attention non fonctionnelle : manque les nouvelles modification de tache (previous, resource...)
    """
    Duplicate a task
    only for moving a product from stockA to stockB
    and produce tasks
    named to True to add old name to given name
    return json response
    """
    taskOrigine = getvalues(factoryid, "task", taskId)
    if named:
        name = name + "_" + taskOrigine["name"]
    if taskOrigine["taskType"] == "taskMoveProductXFromStockAToStockB":
        # taskOrigine = getvalues(factoryid, "taskMoveProductXFromStockAToStockB", taskId)
        try:
            return createTaskMoveProductXFromStockAToStockB(factoryid, name, taskOrigine["productInfo"], taskOrigine["stockAInfo"], taskOrigine["stockBInfo"])
        except:
            return None
    elif taskOrigine["taskType"] == "taskProduce":
        try:
            return createTaskProduce(factoryid, name, taskOrigine["taskName"], taskOrigine["endPartNames"], taskOrigine["listrawparts"], taskOrigine["listinputparts"])
        except:
            return None
    else:
        return None

def defineNewJob(factoryid, name, tasklist):
    """
    Create a new job as a list of task(s)
    return json response
    """
    url = urlTemplateFactory.replace('{factoryid}', factoryid)+'jobdescription'
    data = {
        "name":name,
        "taskList": tasklist,
    }
    response = requests.post(url, json=data)

    return response.json()

def formalize2list(texteoulist):
    if texteoulist:
        if type(texteoulist) == str:
            return [texteoulist]
        if type(texteoulist) == type(u'unicode'):
            return [texteoulist]
        elif type(texteoulist) == list:
            return texteoulist
        elif type(texteoulist) == dict:
            return list(texteoulist.values())
        elif type(texteoulist) == set:
            return list(texteoulist)
        else:
            return []
    return []

def createOperationMoveRobotTo(factoryid, robotId, position, name=None, previous=None):
    """
    Create an operation for moving the robot to a specific point
    """
    # p = DBRef('resource', robotId)
    url = urlTemplateFactory.replace('{factoryid}', factoryid)+'robotmove'

    if isinstance(position, list) or isinstance(position, tuple):
        x = position[0]
        y = position[1]
        theta = position[2]
    else:
        return False

    data = {
        "resourceInfo":robotId,
        # "precedenceOperationInfo":"empty",
        "params": {
            'transform2D': {
                'x':x,
                'y':y,
                'theta':theta
            }
        }
    }
    if len(position)>3:
        data["params"]['stockInfo'] = position[3]
    if name:
        data["name"] = name
    data["precedenceOperationInfo"] = formalize2list(previous)
    response = requests.post(url, json=data)

    return response.json()

def createOperationHuman(factoryid, HumanId, position, texte=None, name=None, previous=None):
    """
    Create an operation for human at a specific point
    """

    if isinstance(position, list) or isinstance(position, tuple):
        x = position[0]
        y = position[1]
        theta = position[2]
    else:
        return False

    url = urlTemplateFactory.replace('{factoryid}', factoryid)+'humanaction'
    data = {
        "resourceInfo":HumanId,
        'transform2D': {
            'x':x,
            'y':y,
            'theta':theta,
        },
    }
    if len(position)>3:
        data['stockInfo'] = position[3]
    data['precedenceOperationInfo'] = formalize2list(previous)
    if name:
        data["name"] = name
    if texte:
        data["params"] = {}
        data['params']['taskstodo'] = formalize2list(texte)
    else:
        data['params']["taskstodo"] = ["Do what is needed"]
            
    response = requests.post(url, json=data)

    return response.json()

def createOperationGrab(factoryid, robotid, positionquater, fonctionrobot="grab", functionparameters='', name=None, previous=None):
    """
    Create an operation for grab an object at a specific point
    """
    # p = DBRef('resource', robotId)

    url = urlTemplateFactory.replace('{factoryid}', factoryid)+'grab'
    data = {
        "resourceInfo":robotid,
        # "precedenceOperationInfo":"empty",
        "params":{
            "position":{
                "position":{
                    "x": positionquater[0][0] , "y":  positionquater[0][1], "z":  positionquater[0][2]
                },
                "rotation":{
                    "qx":  positionquater[1][0], "qy": positionquater[1][1], "qz": positionquater[1][2], "qw": positionquater[1][3]	
                }
            },
            "parameters":functionparameters,
            "function":fonctionrobot
        }   
    }
        
    data['precedenceOperationInfo'] = formalize2list(previous)
    if name:
        data["name"] = name
            
    response = requests.post(url, json=data)

    return response.json()

def createOperationMachine(factoryid, machineid, fonctionmachine="produire", functionparameters='', name=None, previous=None):
    """
    Create an operation for grab an object at a specific point
    """
    # p = DBRef('resource', robotId)

    url = urlTemplateFactory.replace('{factoryid}', factoryid)+'production'
    data = {
        "resourceInfo":machineid,
        # "precedenceOperationInfo":"empty",
        "params":{
            "parameters":functionparameters,
            "function":fonctionmachine
        }   
    }
        
    if name:
        data["name"] = name
    data['precedenceOperationInfo'] = formalize2list(previous)
            
    response = requests.post(url, json=data)

    return response.json()

def createMachine(factoryid, name, liststock, capabilities, link=None, position=None):
    """
    create a machine with name
    return the id
    """
    url = urlTemplateFactory.replace('{factoryid}', factoryid)+'machine'
    data = {
        "name": name,
        "resourceType": "machine",
        "transform2D": { 
                "x": 0, "y": 0, "theta": 0
        },
    }
    if position:
        data["transform2D"] = position
        
    data['stockList'] = formalize2list(liststock)
    data["resourceCapabilityList"] = formalize2list(capabilities)

    if link:
        data["link"] = link
    response = requests.post(url, json=data)

    return response.json()

def createPoste(factoryid, nom, position, tailleposte=[0.7, 0.6, 0.8], taillerobot=[1.0, 0.6, 0.4], link=None ):
    """création d'un poste constitué d'une machine de tailleposte=[x,y,z]
    associé à une zone de stockage de taillerobot en entré et en sortie
    a la position du stock (la machine est décalée en conséquence
    le nez du robot est placé face au coté 'x'
    retourne [idmachine, idstockin, idstockout]"""
    # taille poste 0.7 * 0.6 * 0.8
    # taille robot 1.0 * 0.6 * 0.4
    ecartcentre = (taillerobot[0] + tailleposte[0]) / 2
    xrobot = position["x"]
    yrobot = position["y"]
    trobot = position["theta"] * math.pi / 180
    xmachine = xrobot + ecartcentre * math.cos(trobot)
    ymachine = yrobot + ecartcentre * math.sin(trobot)

    poste={}
    json = createMachine(factoryid, nom, [], [{"category": "production"},], position={"x":xmachine, "y":ymachine, "theta":position["theta"], }, link=link)
    poste["poste"] = json["_id"]

    updateobject(factoryid,"machine",poste["poste"],{"volume":{"dx":0.6, "dy":0.7, "dz":0.8}})
    json = createStock(factoryid, nom + " in", "in", position2d={"x":-ecartcentre, "y":0.0, "theta":0.0, }, link=poste["poste"])
    poste["in"] = json["_id"]
    json = createStock(factoryid, nom + " out", "out", position2d={"x":-ecartcentre, "y":0.0, "theta":0.0, }, link=poste["poste"])
    poste["out"] = json["_id"]
    return poste

def findrealposition(factoryid, parametres):
    try:
        newparametres = parametres["params"]
    except KeyError:
        newparametres = parametres

    pos = newparametres["transform2D"]
    posx = pos['x']
    posy = pos['y']
    theta = pos['theta']
    lien = None
    if "stockInfo" in newparametres:
        stock = getvalues(factoryid, "stock", newparametres['stockInfo'])
        stockpos = stock["transform2D"]
        stox, stoy, stothetadeg, stothetarad = stockpos['x'], stockpos['y'], stockpos['theta'], stockpos['theta']/180*math.pi
        xavant = stox + posx * math.cos(stothetarad) - posy * math.sin(stothetarad)
        yavant = stoy + posy * math.cos(stothetarad) + posx * math.sin(stothetarad)
        tavant = (stothetadeg + theta) % 360
        tavant = tavant if tavant <= 180 else tavant - 360
        if 'link' in stock:
            lien = stock["link"]
        else:
            return {'x':xavant,'y':yavant, 'theta':tavant}
    elif 'link' in newparametres:
        xavant, yavant, tavant = posx, posy, theta
        lien = newparametres["link"]
    while lien:
        machine = getvalues(factoryid, "machine", lien)
        if machine:
            machinepos = machine["transform2D"]
        else:
            return False
        machx, machy, macht, machtrad = machinepos['x'], machinepos['y'], machinepos['theta'], machinepos['theta']/180*math.pi
        xapres = machx + xavant * math.cos(machtrad) - yavant * math.sin(machtrad)
        yapres = machy + yavant * math.cos(machtrad) + xavant * math.sin(machtrad)
        tapres = (macht + tavant) % 360
        tapres = tapres if tapres <= 180 else tapres - 360
        xavant, yavant, tavant = xapres, yapres, tapres
        if 'link' in machine:
            lien = machine['link']
        else:
            lien = None
        return {'x':xavant, 'y':yavant, 'theta':tavant}
    else:
        return {'x':posx, 'y':posy, 'theta':theta}

seturl('http://127.0.0.1:5000/')

if __name__ == "__main__":
    # ret1 = createOrder(factoryid, "Ma référence", "Banane", 150)
    # ret2 = createJob(factoryid, "Ma référence job", "Banane")
    print("done 2")
    # lock = thread.allocate_lock()
    # thread.start_new_thread(myfunction, ("Thread #: 1", 2, lock))
    # thread.start_new_thread(myfunction, ("Thread #: 2", 2, lock))