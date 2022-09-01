import socket
import threading
# import selectors
import pymongo
import Commandes.commandeAPI as commandeAPI

# on suppose le positionnement du serveur mongodb

mongodburl = commandeAPI.urlTemplate[commandeAPI.urlTemplate.find("//")+2:commandeAPI.urlTemplate.find(":5000")]
serverwatchurl = "127.0.0.1"
serverwatchport = 5001

class ServerThread(threading.Thread):
    def __init__(self,clientAddress,clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        print ("New connection added: ", clientAddress)
    def run(self):
        print ("Connection from : ", clientAddress)
        #self.csocket.send(bytes("Hi, This is from Server..",'utf-8'))
        msg = ''
        while True:
            data = self.csocket.recv(2048)
            msg = data.decode()
            if msg=='bye':
              break
            if msg:
                print ("from client", msg)
            self.csocket.send(bytes(msg,'UTF-8'))
        print ("Client at ", clientAddress , " disconnected...")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((serverwatchurl, serverwatchport))
print("Server started on " + serverwatchurl + ":" + str(serverwatchport))
print("Waiting for client request..")
while True:
    server.listen(1)
    clientsock, clientAddress = server.accept()
    newthread = ServerThread(clientAddress, clientsock)
    newthread.start()
# sel = selectors.DefaultSelector()
# # ...
# serveurlocal = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# serveurlocal.bind((serverwatchurl, serverwatchport))
# serveurlocal.listen()
# print('listening on', (serverwatchurl, serverwatchport))
# serveurlocal.setblocking(False)
# sel.register(serveurlocal, selectors.EVENT_READ, data=None)

# def accept_wrapper(sock):
#     conn, addr = sock.accept()  # Should be ready to read
#     print('accepted connection from', addr)
#     conn.setblocking(False)
#     data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
#     events = selectors.EVENT_READ | selectors.EVENT_WRITE
#     sel.register(conn, events, data=data)

# def service_connection(key, mask):
#     sock = key.fileobj
#     data = key.data
#     if mask & selectors.EVENT_READ:
#         recv_data = sock.recv(1024)  # Should be ready to read
#         if recv_data:
#             data.outb += recv_data
#         else:
#             print('closing connection to', data.addr)
#             sel.unregister(sock)
#             sock.close()
#     if mask & selectors.EVENT_WRITE:
#         if data.outb:
#             print('echoing', repr(data.outb), 'to', data.addr)
#             sent = sock.send(data.outb)  # Should be ready to write
#             data.outb = data.outb[sent:]

# while True:
#     events = sel.select(timeout=None)
#     for key, mask in events:
#         if key.data is None:
#             accept_wrapper(key.fileobj)
#         else:
#             service_connection(key, mask)

print("Done")

