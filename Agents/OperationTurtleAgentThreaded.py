import time
import sys
# import os
import glob
import threading
from math import sqrt
import Turtle
import Commandes.commandeAPI as commandeAPI
#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

debugposte = False

if debugposte:
    commandeAPI.urlTemplateFactory = commandeAPI.urlTemplateFactory.replace('robigdata.rorecherche', '127.0.0.1')
    commandeAPI.urlTemplate = commandeAPI.urlTemplate.replace('robigdata.rorecherche', '127.0.0.1')

if len(sys.argv) > 2:
    nom = sys.argv[1]
    Robot = Turtle.Turtle(nom=sys.argv[2])
else:
    nom = "turtle_w1"
    Robot = Turtle.Turtle(nom=nom)

class AgentOperationTurtle(threading.Thread):
    """définition de l'agent gerant les opérations des robots mobiles"""
    def __init__(self, threadID, name, factoryId, myself, dirscripts, lienrobot):
        threading.Thread.__init__(self)
        self.threadid = threadID
        self.name = name
        self.myself = myself
        self.factoryid = factoryId
        self.dirscripts = dirscripts
        self.robot = lienrobot
        self.me_in_database = commandeAPI.getvalues(self.factoryid, "resource", self.myself)
        # self.categories = [x['category'] for x in self.me_in_database["resourceCapabilityList"] if 'category' in x.keys()]
        # for category in self.me_in_database["resourceCapabilityList"]:
        #     if 'category' in category.keys():
        #         self.categories.append(category['category'])
        x, y, theta = self.robot.getposition()
        self.updatepos(x, y, theta)
        # commandeAPI.updateobject(factoryId, "resource", myself, {"transform2D":{"x":x, "y":y, "theta":theta}})
        # if {'category':'grab'} in self.me_in_database["resourceCapabilityList"]: # Specifique aux bras robots
        self.initfunctions()

    def initfunctions(self):
        listescript = glob.glob(self.dirscripts+'/*.ascript')
        self.scripts = {}
        # suppression de toutes les anciennes capability
        # self.me_in_database["resourceCapabilityList"]
        listfonction = [x['category'] for x in self.me_in_database["resourceCapabilityList"] if 'category' in x.keys()]
        for script in listescript:
            newscript = script[script.replace('\\', '/').rfind('/')+1:script.rfind('.')]
            self.scripts.update({newscript:script})
            #(re)creation des capabality
            if newscript not in listfonction:
                self.me_in_database["resourceCapabilityList"].append({'category':newscript})
        commandeAPI.updateobject(self.factoryid, "resource", self.myself, {"resourceCapabilityList":self.me_in_database["resourceCapabilityList"]})
        # [{"category": "transport"}, {"category": "wait"}]
        return

    def updatepos(self, x, y, theta):
        commandeAPI.updateobject(self.factoryid, "resource", self.myself, {"transform2D":{"x":x, "y":y, "theta":theta}})

    def dist(self, x1, y1, x2, y2):
        return sqrt((x1-x2)**2+(y1-y2)**2)

    def run(self):
        while True:
            finded_unseen_operation = commandeAPI.findINfactory(self.factoryid, "operation", operationStatus="toDo", resourceInfo=self.myself)
            for atraiter in finded_unseen_operation:
                commandeAPI.updatestatus(self.factoryid, "operation", atraiter, "toDoAcknowledge")
                operationbase = commandeAPI.getvalues(self.factoryid, "operation", atraiter)
                if operationbase['operationType'] == "robotmove":
                    positiontogo = operationbase['params']['transform2D']
                    commandeAPI.updatestatus(self.factoryid, "operation", atraiter, "doing")
                    self.robot.moveto(positiontogo['x'], positiontogo['y'], positiontogo['theta'])
                    x,y,theta = self.robot.getposition()
                    self.updatepos(x, y, theta)
                    time.sleep(1) # donner le temps à réagir
                    topchrono = 0
                    while self.robot.getstatus() != "Ready":
                        xn,yn,thetan = self.robot.getposition()
                        topchrono += 1
                        if self.dist(x, y, xn, yn) > 0.01 or abs(theta - thetan) > 3: # 1cm ou 3° => Ca bouge
                            topchrono = 0
                            self.updatepos(xn, yn, thetan)
                        x = xn ; y = yn ; theta = thetan
                        time.sleep(0.3)
                        if topchrono > 30/0.3:
                            break
                    if self.dist(positiontogo['x'], positiontogo['x'], x, y) < 0.02  and abs(positiontogo['theta'] - theta) < 3:
                        commandeAPI.updatestatus(self.factoryid, "operation", atraiter, "done")
                    else:
                        commandeAPI.updatestatus(self.factoryid, "operation", atraiter, "error")
                    # il faut ajouter un timeout

                elif operationbase['operationType'] == "grab":
                    operationtodo = operationbase['params']['function']
                    # peut on faire l'action ?
                    if operationtodo in self.scripts.keys() or operationtodo == 'grab' or operationtodo == 'wait':
                        # si oui ==> on fait l'action
                        commandeAPI.updatestatus(self.factoryid, "operation", atraiter, "doing")
                        # quand c'est fait : on le dit
                        # robot.sendcommand("ur5_t_e\\grab.ascript", delta_saisie=0.10)
                        if operationtodo in self.scripts.keys():
                            print("non fonctionnel")
                            # self.robot.sendcommand(self.scripts[operationtodo], delta_saisie=0.10)
                        elif operationtodo == 'wait':
                            print("wait")
                        elif operationtodo == 'grab':
                            print("grab fictif")
                    commandeAPI.updatestatus(self.factoryid, "operation", atraiter, "done")
                else:
                    # si non ==> on informe la base
                    commandeAPI.updatestatus(self.factoryid, "operation", atraiter, "error")
            time.sleep(1)

if __name__ == "__main__":
    Regeneration = False # régénération du turtle et de sa liste d'opération
    Regenerationope = True
    print("Launch Robot Agent " + nom + " connected to database " + commandeAPI.urlTemplate)
    factoryidentity = commandeAPI.findfactory(name="Demo Turtle Real")[0]
    if Regeneration:
        robot = commandeAPI.findINfactory(factoryidentity, "robot", name=nom)
        if robot:
            robot = robot[0]
            commandeAPI.deletepart(factoryidentity, typedata="operation", resourceInfo=robot)
            commandeAPI.deletepart(factoryidentity, "robot", name=nom)
        json = commandeAPI.createRobotResource(factoryidentity, "turtle_w1", "turttlew", [{"category": "transport"}, {"category": "wait"}])
        robot = json["_id"]
        commandeAPI.updateobject(factoryidentity, "resource", robot, {"transform2D":{"x":2.0, "y":2.1, "theta":180.0}})
    else:
        robot = commandeAPI.findINfactory(factoryidentity, "robot", name=nom)[0]
        if Regenerationope:
            commandeAPI.deletepart(factoryidentity, typedata="operation", resourceInfo=robot)

    robot_agent = AgentOperationTurtle(1, "Turtel Waffle 1", factoryidentity, robot, nom, Robot)
    operation1 = commandeAPI.createOperationMoveRobotTo(factoryidentity, robot, (3.0, 3.0, 0.0))["_id"] # vertical
    operation2 = commandeAPI.createOperationMoveRobotTo(factoryidentity, robot, (5.0, 5.0, 180.0), previous=operation1)["_id"] # vertical


    robot_agent.start()
    print("done")
    robot_agent.join()
    print("end")
