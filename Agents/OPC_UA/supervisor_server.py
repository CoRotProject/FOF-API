import sys
sys.path.insert(0, "..")
from opcua import  Server
import pickle 
import time

class supervisor_server():
    '''The supervisor server that communicates with the external system. '''
    def __init__(self,name, ip,):
        self.ip = ip
        self.name = name
        self.server = Server()
        self.server.set_endpoint("opc.tcp://"+self.ip+":5840")
        uri = "festo_supervisor"
        self.idx = self.server.register_namespace(uri)
        self.objects = self.server.get_objects_node()
        
    def push_all_node(self):
        with open(self.name+'_var.pickle', 'rb') as handle:
            self.unserialized_data = pickle.load(handle)
        key = list(self.unserialized_data.keys())
        for i in range(0,len (self.unserialized_data)):
            node = self.objects.add_object(self.idx,key[i])
            node_val = node.add_variable(self.idx, key[i], self.unserialized_data[key[i]])
            node_val.set_writable()
        print(self.unserialized_data)

    def run(self):
        self.server.start()

    
    def terminate(self):
         """clean stop"""
         self.server.stop()
         print(self.unserialized_data)

            

if __name__ == "__main__":

    supervisor = supervisor_server(name ='plc_man2',ip="192.168.0.210")
    supervisor.push_all_node()
    supervisor.run()
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        supervisor.terminate()
    print("killed")
