from ssl import _create_unverified_context
import time
import sys
import TaskAgent
import Commandes.commandeAPI as commandeAPI
import CNC
#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

simulated = True

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

### Agent de lecture des operations correspondantes à une resources d'une usine => création d'une FIFO d'opération valide 

try:
    nomfactory = sys.argv[2]
except IndexError:
    nomfactory = "Factory LINEACT Test Fabrice"
print("Used factory: ", nomfactory)

try:
    nommachine = sys.argv[3]
except IndexError:
    nommachine = "CERI_CNC"
print("Used resource: ", nommachine)

try:
    nomporte = sys.argv[4]
except IndexError:
    nomporte = "PorteCNC"
print("Used resource: ", nomporte)

runningtask = None

class TaskCERI_CNC(TaskAgent.TaskRunning):
    def __init__(self, threadID, name, thefactoryid, mainresourceid, machinereel, porteid, strictmode=False):
        TaskAgent.TaskRunning.__init__(self, threadID, name, thefactoryid, mainresourceid)
        self.strictmode = strictmode
        self.porteid = porteid
        self.stateinput = "empty"
        self.connexion = machinereel
        self.myself = commandeAPI.getvalues(self.factoryid, "machine", self.resource)
        stocks = self.myself["stockList"]
        stockA = commandeAPI.getvalues(self.factoryid, 'stock', stocks[0])
        if stockA["name"] == "CNC_inout":
            self.stockinout = stocks[0]
            self.stockintern = stocks[1]
        else:
            self.stockinout = stocks[1]
            self.stockintern = stocks[0]

        if not simulated:
            print("unable to autoset warmup status")
            print("be sure that input stock and machine are empty")
            print("type OK, when is ready")
            print("type anything else to launch a running sequence in order to empty the machine")
            out = "not ready"
            while not out.upper() == "OK":
                out = input("? : ")
                if not out.upper() == "OK":
                    self.connexion.pulsestart()
        
        # on vide les stocks ==> produit apatride
        listtoremove = commandeAPI.findINfactory(self.factoryid, "product", link=self.stockinout)
        listtoremove.extend(commandeAPI.findINfactory(self.factoryid, "product", link=self.stockintern))
        for objet in listtoremove:
            commandeAPI.updateobject(self.factoryid, "product", objet, {'link':None})
        # commandeAPI.deletepart(self.factoryid, typedata="product", link=self.stockinout)
        # commandeAPI.deletepart(self.factoryid, typedata="product", link=self.stockintern)

    def update(self):
        """update position and status"""
        self.state = self.connexion.getstatus()
        status = self.state["CNC"]
        if status == "ready":
            self.status = "free"
        else:
            self.status = "busy"

    def tasktooperation(self,taskid, taskcontent):
        if self.validoperations:
            return False
        switchvalue = taskcontent["taskType"]
        self.operationlist = []
        if switchvalue == "Task":
            print("generictask")
        elif switchvalue == "taskProduce":
            print("produce")
            # taskfine = commandeAPI.getvalues(self.factoryid,"produce",taskid)
            # productid = commandeAPI.findINfactory(self.factoryid,"product",link=self.stockinout)[0]
            self.operationlist.append([commandeAPI.createOperationMachine(self.factoryid, self.resource, name="Usinage")["_id"], "produce" ])
            commandeAPI.updateobject(self.factoryid, "task", taskid, {"operationInfoList":[self.operationlist[-1][0]]})
        elif switchvalue == "taskMoveProductXFromStockAToStockB":
            print("move from place to place")
        elif switchvalue == "taskHuman":
            print("Human")
        retour = False
        for operation in self.operationlist:
            if operation[0]:
                commandeAPI.updatestatus(factoryid, "operation", operation[0], "toDo")
            retour = True

        self.validoperations = retour
        return retour
    
    def operation(self,operation):
        if operation[1] == 'moveproduct':
            commandeAPI.updateobject(self.factoryid, "product", operation[2], {"link":operation[3]})
            return True
        elif operation[1] == 'produce':
            print('produce ope run')
            getproductin = commandeAPI.findINfactory(self.factoryid, typedata="product", link=self.stockinout)
            getproductintern = commandeAPI.findINfactory(self.factoryid, typedata="product", link=self.stockintern)
            try:
                product = commandeAPI.getvalues(self.factoryid,"product",getproductin[0])
            except IndexError:
                print("input stock empty")
                return False

            selectedprg = "zzzzzzzz"
            for val,operation in enumerate(product["operationToDoList"]):
                try:    
                    quelop = operation['operation']
                    status = operation['status']
                except KeyError:
                    continue
                if quelop == 'CNC' and status == 'toDo':
                    try:    
                        program = operation['parameters']
                    except KeyError:
                        selectedprg = "default"
                        valout = val
                        break
                    if program[0] < selectedprg:
                        selectedprg = program[0]
                        valout = val

            if self.strictmode:
                if not selectedprg == "zzzzzzzz":
                    # yes, i can do it
                    product["operationToDoList"][valout]["status"] = "doing"
                    commandeAPI.updateobject(self.factoryid, "product", getproductin[0], {"operationToDoList":product["operationToDoList"]})
            elif selectedprg == "zzzzzzzz":
                # add CNC in doing status
                product["operationToDoList"].append({"operation":"CNC", "status":"doing"})
                commandeAPI.updateobject(self.factoryid, "product", getproductin[0], {"operationToDoList":product["operationToDoList"]})
                selectedprg = "default" #run prg by default
                valout = len(product["operationToDoList"]) - 1

            if selectedprg == "zzzzzzzz":
                print("error machining no valid object in strict mode {}".format(getproductin))
                return False
            else:
                commandeAPI.updateobject(self.factoryid, "product", getproductin[0], {"link":self.stockintern})
                if getproductintern:
                    commandeAPI.updateobject(self.factoryid, "product", getproductintern[0], {"link":self.stockinout})
                print("launch machinig to {} with prg {}".format(getproductin[0],selectedprg))
                # RUN ICI possibilié de creer des programmes selectedprg
                # Take door resource
                while not commandeAPI.takereservation(self.factoryid,self.porteid, self.resource):
                    time.sleep(1.0)
                print("waiting for last process", end="")
                while self.connexion.getstatus()['CNC'] == 'busy':  # en cas de fonctionnement en cours
                    time.sleep(1.0)
                    print(".", end="")
                self.connexion.run()
                time.sleep(2.0)
                print("\nwaiting for door", end="")
                while self.connexion.getstatus()['door'] == 'close':
                    time.sleep(1.0)
                    print(".", end="")
                commandeAPI.releasereservation(self.factoryid,self.porteid, self.resource)
                print("\nwaiting for end process", end="")
                while self.connexion.getstatus()['CNC'] == 'busy':
                    time.sleep(1.0)
                    print(".", end="")
                print(" ")
                product["operationToDoList"][valout]["status"] = "done"
                commandeAPI.updateobject(self.factoryid, "product", getproductin[0], {"operationToDoList":product["operationToDoList"]})
                # retournement ?
                if commandeAPI.takereservation(self.factoryid,self.porteid, self.resource): # la resource est libre
                    if not commandeAPI.findINfactory(self.factoryid, typedata="product", link=self.stockinout): # il y a rien en entree
                        print("retournement a vide")
                        self.connexion.run() #on lance "vers la sortie"
                        time.sleep(2.0)
                        while self.connexion.getstatus()['door'] == 'close':
                            print("\nwaiting for door")
                            time.sleep(1.0)
                        commandeAPI.updateobject(self.factoryid, "product", getproductin[0], {"link":self.stockinout})
                    commandeAPI.releasereservation(self.factoryid,self.porteid, self.resource)
                # un robot a certainement pris le lock
                print("process ended")
                return True
        elif operation[1] == 'grab':
            print('grab function ' + operation[3])
            time.sleep(1)
            return False
        return False

if __name__ == "__main__":

    creationtest = False
    runtest = False

    factoryid = commandeAPI.findfactory(name=nomfactory)[0]
    Regeneration = False
    print("Launch Task Agent " + nommachine + commandeAPI.urlTemplate)

    resource = commandeAPI.findINfactory(factoryid, "resource", name=nommachine)[0]
    portecnc = commandeAPI.findINfactory(factoryid, "resource", name=nomporte)[0]

    if simulated:
        cncsimulator = CNC.CNCSimulate()
        cncsimulator.start()

    time.sleep(1.0)
    machinereel = CNC.CNC(nom=nommachine)

    taskagent = TaskAgent.AgentTask(1, nomfactory+" "+nommachine, factoryid, resource)
    runningtask = TaskCERI_CNC(1, nomfactory+" "+nommachine, factoryid, resource, machinereel, portecnc, strictmode=True)
    taskagent.runningtask = runningtask

    machineid = commandeAPI.findINfactory(factoryid, "machine", name=nommachine)[0]
    machine = commandeAPI.getvalues(factoryid, "machine", machineid)
    stockid = machine["stockList"][0]
    stock = commandeAPI.getvalues(factoryid, "stock", stockid)
    if stock["mode"] == "internal":
        stockinterneid = stockid
        stockinterne = stock
        stockinoutid = machine["stockList"][1]
        stockinout = commandeAPI.getvalues(factoryid, "stock", stockinoutid)
    else:
        stockinoutid = stockid
        stockinout = stock
        stockinterneid = machine["stockList"][1]
        stockinterne = commandeAPI.getvalues(factoryid, "stock", stockinterneid)    #creation test

    if creationtest:
        productid = commandeAPI.createProduct(factoryid, "Raw_Part N_1", "Raw_Part")["_id"]
        commandeAPI.updateobject(factoryid, "product", productid, {"operationToDoList":[{"operation":"CNC", "status":"toDo", "parameters":["Face1"]},{"operation":"CNC", "status":"toDo", "parameters":["Face2"]}]})
        commandeAPI.updateobject(factoryid, "product", productid, {"link":stockinoutid})
        task = commandeAPI.createTaskProduce(factoryid,"Tache B","Produce","Intermediate_Part N_1",[],productid, resource=machineid)["_id"]
    elif runtest:
        productid = commandeAPI.findINfactory(factoryid, "product", name="Raw_Part N_1")[0]
        commandeAPI.updateobject(factoryid, "product", productid, {"link":stockinoutid, "operationToDoList":[{"operation":"CNC", "status":"toDo", "parameters":["Face1"]},{"operation":"CNC", "status":"toDo", "parameters":["Face2"]}]})
        task = commandeAPI.findINfactory(factoryid, "task", name="Tache B")[0]



    taskagent.start()
    runningtask.start()
    time.sleep(1.0)
    if runtest:
        commandeAPI.updatestatus(factoryid, "task", task, "toDo")

    print("done")
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        taskagent.terminate()
        runningtask.terminate()
        if simulated:
            cncsimulator.terminate()
    print("killed")
