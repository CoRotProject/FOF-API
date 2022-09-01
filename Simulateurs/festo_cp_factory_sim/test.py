import json
import pickle 
from multiprocessing import Process,Pipe
# Make it work for Python 2+3 and with Unicode
import io
try:
    to_unicode = unicode
except NameError:
    to_unicode = str
    
global num
f = open('poste_man2.json')
 
# returns JSON object as
# a dictionary
data = json.load(f)

'''for i in range(len(data['poste_man2'])):
    print(data['poste_man2'][i]['child'],'\n')'''


def get_child(parent):

    for i in range(len(parent)):
        #print(parent[i]['child'],'\n')
        if parent[i]['child'] == []:
            print(parent[i]['name'],': ')
        elif parent[i]['child'] != []:
            for j in range(len(parent[i]['child'])):
                print(parent[i]['name'],':',parent[i]['child'][j]['name'])
            get_child(parent[i]['child'])


#get_child(data['poste_man2'])

data = {
    'name':['in_belt1', 'pres_RFID1', 'RFID1', 'out_belt1', 'in_belt2', 'pres_RFID2', 'RFID2','cap_sen_belt2','cap_sen_belt2','out_belt2','int_half_belt2','out_half_belt2'],
    'value':[0,1,0,1,0,1,0,1,0,1,0,1],
    'Rising_front':[0,0,0,0,0,0,0,0,0,0,0,0]
}

with open('poste_man2.pickle', 'wb') as handle:
    pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('poste_man2.pickle', 'rb') as handle:
                unserialized_data = pickle.load(handle)

def f(child_conn):
    msg = "Hello"
    child_conn.send(msg)
    child_conn.close()

print(unserialized_data)