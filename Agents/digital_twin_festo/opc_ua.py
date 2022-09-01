import sys
sys.path.insert(0, "..")
from opcua import Client 
import threading
import time


class opc_module(threading.Thread):
    def __init__(self,name, addresse,):
        threading.Thread.__init__(self)
        self.addresse = addresse
        self.name = name
        self.client = Client("opc.tcp://"+self.addresse)
        self.client.connect()
        self.running = True
        print("client is connected to opc ua of "+self.name+'\n')
        #print('the available namespace', self.client.get_namespace_array(),'\n')
        self.objects = self.client.get_objects_node()
        self.first_branch = self.objects.get_children()
        #print(self.first_branch,'\n')
        self.ServerInterfaces = self.objects.get_children()[3]
        self.Branch_OPC = self.ServerInterfaces.get_children()[0]
        self.myvarlist = self.Branch_OPC.get_children()
        #print(self.myvarlist,'\n')
        self.data = {}
        self.all_var_name =[]
        for i in range(1,len(self.myvarlist)):
                #print(self.myvarlist[i].get_browse_name().to_string()[2:-1])
                var_name=self.myvarlist[i].get_browse_name().Name
                self.all_var_name.append(var_name)
                self.data[var_name] = None

        #print(self.data)

    def get_data(self):
        return self.data

    def run(self):
        while self.running:
            for i in range(1,len(self.myvarlist)):
                var_value = self.Branch_OPC.get_children()[i]
                #print(var_value.get_browse_name().to_string(),'  =  ', var_value.get_value())
                self.data[self.all_var_name[i-1]]=[var_value.get_value(),var_value.nodeid.Identifier]
                
    
    def terminate(self):
         """clean stop"""
         self.client.disconnect()
         self.running = False
         print(self.data)

            

if __name__ == "__main__":

    plc_man2 = opc_module(name ='plc_man2',addresse="10.191.76.20:4048")
    plc_man2.start()
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        plc_man2.terminate()
    print("killed")
