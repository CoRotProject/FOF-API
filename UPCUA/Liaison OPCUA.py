# coding: utf8
# Copyright 2020 Fabrice DUVAL
# import requests
import os
import sys
import time
# import random
import base64
import math
# from pyquaternion import Quaternion

import Commandes.commandeAPI as commandeAPI
from opcua.common.type_dictionary_buider import DataTypeDictionaryBuilder, get_ua_class
from opcua import Client, ua
import threading


# mir_node = client.get_node("ns=2;i=70") ## check nodeid

link_OP_Node ={"m11":"ns=2;i=65", "m12":"ns=2;i=66", "m21":"ns=2;i=67", "m22":"ns=2;i=68", "m31":"ns=2;i=69", "m32":"ns=2;i=70",
    "o11":"ns=2;i=65", "o12":"ns=2;i=66", "p11":"ns=2;i=65", "p12":"ns=2;i=66", "p13":"ns=2;i=65", "p21":"ns=2;i=66", "p22":"ns=2;i=65", "p23":"ns=2;i=66"}

#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()
else:
    factoryid = commandeAPI.findfactory(name="Factory Said")[0]

print(os.getcwd())

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

dict = {}

class SubHandler(object):

    def datachange_notification(self, node, val, data):
        dict[node] = val

    def event_notification(self, event):
        print("Python: New event", event)

def euler_to_quaternion(x,y,z):

    q =[]
    chr = math.cos(x/2)
    shr = math.sin(x/2)
    chp = math.cos(y/2)
    shp = math.sin(y/2)
    chd = math.cos(z/2)
    shd = math.cos(z/2)

    q.append((chd*chp*shr - shd*shp*chr))
    q.append((chd*shp*chr - shd*chp*shr))
    q.append((shd*chp*chr - chd*shp*shr))
    q.append((chd*chp*chr - shd*shp*shr))

    return q

def publish():

    oper = {}
    # for key in ["m11", "m12", "m21", "m31", "m32"]:
    #     oper[key] = link_OP_Node[key][1].get_value()


    # oper_msg_m11 = m11_node.get_value()
    # oper_msg_m12 = m12_node.get_value()
    # oper_msg_m21 = m21_node.get_value()
    # oper_msg_m22 = m22_node.get_value()
    # oper_msg_m31 = m31_node.get_value()
    # oper_msg_m32 = m32_node.get_value()

    mir_msg = mir[1].get_value()

    while True:
        for key in ["m11", "m12", "m21", "m22", "m31", "m32"]:
            opermessage = link_OP_Node[key][1].get_value()
            opermessage.status = commandeAPI.getstatus(factoryid, "operation", link_OP_Node[key][2])
            link_OP_Node[key][1].set_value(opermessage)
    #     oper[key] = link_OP_Node[key][1].get_value()

        # oper_msg_m11.status = commandeAPI.getstatus(factoryid, "operation", link_OP_Node["m11"][2])
        # # oper_msg_m11.status = commandeAPI.getstatus(factoryid, "operation", m11["_id"])
        # m11_node.set_value(oper_msg_m11)
        
        # oper_msg_m12.status = commandeAPI.getstatus(factoryid, "operation", m12["_id"])
        # m12_node.set_value(oper_msg_m12)

        # oper_msg_m21.status = commandeAPI.getstatus(factoryid, "operation", m21["_id"])
        # m21_node.set_value(oper_msg_m21)

        # oper_msg_m22.status = commandeAPI.getstatus(factoryid, "operation", m22["_id"])
        # m22_node.set_value(oper_msg_m21)

        # oper_msg_m31.status = commandeAPI.getstatus(factoryid, "operation", m31["_id"])
        # m31_node.set_value(oper_msg_m22)

        # oper_msg_m32.status = commandeAPI.getstatus(factoryid, "operation", m32["_id"])
        # m32_node.set_value(oper_msg_m22)


        mir_infos = commandeAPI.getstatus(factoryid, "robot", mir[2])
        mir_msg.Pose.Point.x = mir_infos['transform2D']['x']
        mir_msg.Pose.Point.y = mir_infos['transform2D']['y']
        th = mir_infos['transform2D']['theta']
        q = euler_to_quaternion(0,0,th)
        mir_msg.Pose.Quaternion.z = q[2]
        mir_msg.Pose.Quaternion.w = q[3]
        mir[1].set_value(mir_msg)
        time.sleep(1.0)

        ### if database used to store only
        # commandeAPI.getstatus(factoryid, "operation", o11["_id"])
        # commandeAPI.getstatus(factoryid, "operation", o12["_id"])
        # commandeAPI.getstatus(factoryid, "operation", p11["_id"])
        # commandeAPI.getstatus(factoryid, "operation", p12["_id"])
        # commandeAPI.getstatus(factoryid, "operation", p13["_id"])
        # commandeAPI.getstatus(factoryid, "operation", p21["_id"])
        # commandeAPI.getstatus(factoryid, "operation", p22["_id"])
        # commandeAPI.getstatus(factoryid, "operation", p23["_id"])


def subscribe():


    # while True:

    #     status = dict[o11_node]
    #     commandeAPI.updateobject(factoryid, "operation", o11, {'status':status})
    #     status = dict[o12_node]
    #     commandeAPI.updateobject(factoryid, "operation", o12, {'status':status})
    #     status = dict[p11_node]
    #     commandeAPI.updateobject(factoryid, "operation", p11, {'status':status})
    #     status = dict[p12_node]
    #     commandeAPI.updateobject(factoryid, "operation", p12, {'status':status})
    #     status = dict[p13_node]
    #     commandeAPI.updateobject(factoryid, "operation", p13, {'status':status})
    #     status = dict[p21_node]
    #     commandeAPI.updateobject(factoryid, "operation", p21, {'status':status})
    #     status = dict[p22_node]
    #     commandeAPI.updateobject(factoryid, "operation", p22, {'status':status})
    #     status = dict[p23_node]
    #     commandeAPI.updateobject(factoryid, "operation", p23, {'status':status})

        ### if o11 is done m12 is set to toDo
        ### remove anteriorities
    return True 

if __name__ == "__main__":

    ### initialisation operation and resources in the server
    url_0 = "opc.tcp://localhost:4840"  # IP localhost
    url_1 = "opc.tcp://169.254.204.230:4840"  # IP Ethernet
    url_2 = "opc.tcp://192.168.56.1:4840"  # IP Ethernet
    url = url_2

    client= Client(url)
    client.connect()
    client.load_type_definitions()

    # HMI = client.get_node("ns=2;i=42")
    mir=["ns=2;i=70", client.get_node("ns=2;i=70"), commandeAPI.findINfactory(factoryid,'robot', {"name":"mir100_Arm"})[0]]
    for nom, noeud in link_OP_Node.item():
        link_OP_Node[nom] = [noeud, client.get_node(noeud), commandeAPI.findINfactory(factoryid,'operation', {"name":nom})[0]]
        

    #hmi = HMI.get_value()

    handler = SubHandler()
    sub = client.create_subscription(0, handler)

    # handle_hmi = sub.subscribe_data_change(HMI)

    t1 = threading.Thread(target = publish, name = 'Publish_data')
    t1.daemon = True
    t1.start()

    t2 = threading.Thread(target = subscribe, name = 'Subscribe_status')
    t2.daemon = True
    t2.start()
