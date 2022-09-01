# coding: utf8
# Copyright 2021 Fabrice DUVAL
import time
import threading
# import imp
import sys
import queue
from math import sqrt
import CNC
import Commandes.commandeAPI as commandeAPI

if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

nomfactory = "Factory CERI"
nommachine = "CERI_CNC"
simulate = True

class AgentProduceCNC(threading.Thread):
    """status possible : offline, free, busy, error
    """
    def __init__(self, nom, lienbdd, machinebdd, lienmachine, opvalidfifo, retbasefifo, strictmode = False, simumode = False):
        """lienbdd : id of factory, machinebdd : machine id, lienmachine : link to machine class, opvalidfifo : Queue of valid moveto, retbasefifo : link to update op status"""
        threading.Thread.__init__(self)
        self.name = nom
        self.factoryid = lienbdd
        self.machinebdd = machinebdd
        self.connexion = lienmachine
        self.operationlist = opvalidfifo
        self.fifobase = retbasefifo
        self.strictmode = strictmode # if True, objetc need to have "CNC" in toDo state in operationToDoList

        self.machineinbdd = commandeAPI.getvalues(self.factoryid, 'machine', self.machinebdd)
        stocks = self.machineinbdd["stockList"]
        stockA = commandeAPI.getvalues(self.factoryid, 'stock', stocks[0])
        if stockA["name"] == "CNC_inout":
            self.stockinout = stocks[0]
            self.stockintern = stocks[1]
        else:
            self.stockinout = stocks[1]
            self.stockintern = stocks[0]

        self.status = 'offline'
        self.state = {}
        self.enmission = False
        # self.infomission = []
        self.operationencours = []
        self.update()
        self.running = True
        if not simumode:
            print("unable to autoset warmup status")
            print("be sure that input stock and machine are empty")
            print("type OK, when is ready")
            print("type anything else to launch a running sequence in order to empty the machine")
            out = "not ready"
            while not out.upper() == "OK":
                out = input("? : ")
                if not out.upper() == "OK":
                    self.connexion.pulsestart()
        #cleaning database
        commandeAPI.deletepart(self.factoryid, typedata="product", link=self.stockinout)
        commandeAPI.deletepart(self.factoryid, typedata="product", link=self.stockintern)

    def update(self):
        """update position ans status"""
        self.state = self.connexion.getstatus()
        status = self.state["CNC"]
        if status == "ready":
            self.status = "free"
        else:
            self.status = "busy"

    def run(self):
        nbturn = 0
        product = {}
        numero = -1
        stockin = 0
        while self.running:
            self.update()
            if self.status == "free":
                if self.enmission: # mission en cours et free => look for end of production
                    self.fifobase.put((self.operationencours[0], 'done')) # 
                    self.enmission = False
                    self.operationlist.task_done()
                    if numero >= 0:
                        product["operationToDoList"][numero]["status"] = "done"
                        commandeAPI.updateobject(self.factoryid, "product", stockin, {"operationToDoList":product["operationToDoList"]})
                    nbturn = 0
                else: # no running mission
                    if self.operationlist.empty(): # no pending mission
                        if nbturn == 1: # limit "free" printing
                            print("free")
                        elif nbturn >= 20:
                            nbturn = 0
                        nbturn += 1
                    else: #there is a least 1 valid mission
                        self.status = 'busy'
                        self.enmission = True
                        self.operationencours = self.operationlist.get()
                        self.fifobase.put((self.operationencours[0], 'doing'))

                        getproductin = commandeAPI.findINfactory(self.factoryid, typedata="product", link=self.stockinout)
                        getproductout = commandeAPI.findINfactory(self.factoryid, typedata="product", link=self.stockintern)
                        stockin = None # stockin considerate as empty
                        stockout = None # stockinternal considerate as empty
                        numero = -1 # nothing in stock by default
                        if getproductin:
                            stockin = getproductin[0]
                            # Does the product need CNC ?
                            product = commandeAPI.getvalues(self.factoryid,"product",getproductin[0])
                            try:
                                numero = [x['operation'] for x in product["operationToDoList"]].index('CNC')
                            except KeyError:
                                # no operation in operationToDoList
                                numero = -2
                            except ValueError:
                                # no CNC in operation
                                numero = -3
                            
                            if numero >= 0:
                                if self.strictmode and product["operationToDoList"][numero]["status"] != "toDo":
                                    numero == -1
                                else:
                                    # yes, i can do it
                                    product["operationToDoList"][numero]["status"] = "doing"
                                    commandeAPI.updateobject(self.factoryid, "product", stockin, {"operationToDoList":product["operationToDoList"]})
                            elif numero < 0:
                                if not self.strictmode: # if strict ==> error
                                    # add CNC in doing status
                                    product["operationToDoList"].append({"operation":"CNC", "status":"doing"})
                                    commandeAPI.updateobject(self.factoryid, "product", stockin, {"operationToDoList":product["operationToDoList"]})
                                    numero = len(product["operationToDoList"]) - 1
                            if numero < 0:
                                print("error machinig no valid object in strict mode {}".format(stockin))
                            else:
                                commandeAPI.updateobject(self.factoryid, "product", stockin, {"link":self.stockintern})
                                print("launch machinig to {}".format(stockin))
                        if getproductout:
                            stockout = getproductout[0]
                            print("try  to release {}".format(stockout))
                        if numero < -1: # no valid object ==> Operation error
                            self.status = 'error'
                            self.enmission = False
                            self.fifobase.put((self.operationencours[0], 'error'))
                        else:
                            self.connexion.run()
                            nbrm = commandeAPI.deletepart(self.factoryid, typedata="product", link=self.stockinout) #en cas d'erreur de stock 
                            if nbrm > 0:
                                print("{} false stockin removed".format(nbrm))
                            if stockout:
                                commandeAPI.updateobject(self.factoryid, "product", stockout, {"link":self.stockinout})
                            if numero < 0:
                                # no runnig object => end of operation
                                time.sleep(5.0) # time to return object in CNC
                                self.status = 'free'
                                self.enmission = False
                                self.fifobase.put((self.operationencours[0], 'done')) # empty mission, no need to wait
                        time.sleep(0.5) # donner le temps à réagir

            time.sleep(1)

    def terminate(self):
        """clean stop"""
        print("agent move killed")
        self.running = False

class testoutput(threading.Thread):
    """only to print output of fifo"""
    def __init__(self, nom, retbasefifo):
        threading.Thread.__init__(self)
        self.name = nom
        self.fifobase = retbasefifo
        self.running = True

    def run(self):
        """loop of fifo test"""
        nbturn = 0
        while self.running:
            if self.fifobase.empty(): # no pending mission
                if nbturn == 1: # limit "free" printing
                    print("noreturn")
                elif nbturn >= 20:
                    nbturn = 0
                nbturn += 1
            else:
                nbturn = 0
                print(self.fifobase.get())
            time.sleep(2)

    def terminate(self):
        """clean stop"""
        print("agent test killed")
        self.running = False

if __name__ == "__main__":
    Regenerationope = False
    print("Launch CNC Machine Agent " + nommachine + " connected to database " + commandeAPI.urlTemplate)

    machinereel = CNC.CNC(nom=nommachine)

    opfifo = queue.Queue() # create FIFO of valide operation
    retfifo = queue.Queue() # create FIFO of return value for database

    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
    machinebase = commandeAPI.findINfactory(factoryid, "machine", name=nommachine)[0]

    machine_agent = AgentProduceCNC(nomfactory+" "+nommachine, factoryid, machinebase, machinereel, opfifo, retfifo)
    fifo_agent = testoutput("fifo output", retfifo)

    opfifo.put(["1"])

    if simulate:
        cncsimulator = CNC.CNCSimulate()
        cncsimulator.start()

    machine_agent.start()
    fifo_agent.start()
    print("done")
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        machine_agent.terminate()
        fifo_agent.terminate()
        if simulate:
            cncsimulator.terminate()
    print("killed")
