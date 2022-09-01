import Commandes.commandeAPI as commandeAPI
import time

#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()
else:
    factoryid = commandeAPI.findfactory(name="Factory Said")[0]

link_OP_Node ={"m11":"ns=2;i=65", "m12":"ns=2;i=66", "m21":"ns=2;i=67", "m22":"ns=2;i=68", "m31":"ns=2;i=69", "m32":"ns=2;i=70",
    "o11":"ns=2;i=65", "o12":"ns=2;i=66", "p11":"ns=2;i=65", "p12":"ns=2;i=66", "p13":"ns=2;i=65", "p21":"ns=2;i=66", "p22":"ns=2;i=65", "p23":"ns=2;i=66"}

for nom, noeud in link_OP_Node.item():
    link_OP_Node[nom] = [noeud, commandeAPI.findINfactory(factoryid,'operation', {"name":nom})[0]]

commandeAPI.updateobject(factoryid, "operation", link_OP_Node["m11"][2],  "toDo")

##update status check if status updates are automatic
## set status to toDo mxx
while not commandeAPI.getstatus(factoryid, "operation", link_OP_Node["o11"][2]) == 'Done':
    time.sleep(1.0)
commandeAPI.updateobject(factoryid, "operation", link_OP_Node["m12"][2],  "toDo")

while not commandeAPI.getstatus(factoryid, "operation", link_OP_Node["p11"][2]) == 'Done':
    time.sleep(1.0)
commandeAPI.updateobject(factoryid, "operation", link_OP_Node["m21"][2],  "toDo")

while not commandeAPI.getstatus(factoryid, "operation", link_OP_Node["p13"][2]) == 'Done':
    time.sleep(1.0)
commandeAPI.updateobject(factoryid, "operation", link_OP_Node["m22"][2],  "toDo")

while not commandeAPI.getstatus(factoryid, "operation", link_OP_Node["p21"][2]) == 'Done':
    time.sleep(1.0)
commandeAPI.updateobject(factoryid, "operation", link_OP_Node["m31"][2],  "toDo")

while not commandeAPI.getstatus(factoryid, "operation", link_OP_Node["p23"][2]) == 'Done':
    time.sleep(1.0)
commandeAPI.updateobject(factoryid, "operation", link_OP_Node["m32"][2],  "toDo")

