#-*- coding: utf-8 -*-
# import os
# import socket
# import threading
from flask import Flask, send_from_directory
import watchfunctions
# import selectors
# import pymongo
import Commandes.commandeAPI as commandeAPI

# on suppose le positionnement du serveur mongodb

mongodburl = commandeAPI.urlTemplate.split('://')[-1].split(':')[0]
serverwatchurl = "127.0.0.1"
serverwatchport = 5001

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"
@app.route('/favicon.ico')
def favicon():
    # return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

app.add_url_rule('/none/', view_func=watchfunctions.none)
app.add_url_rule('/factory/<factoryid>', view_func=watchfunctions.operation)
app.add_url_rule('/factory/<factoryid>/operation/<opidentity>', view_func=watchfunctions.operation)
app.add_url_rule('/factory/<factoryid>/task/<tidentity>', view_func=watchfunctions.task)

# if len(sys.argv)>1:
#     print('run with argument',sys.argv[1])
#     if not False in [c in "0123456789." for c in sys.argv[1]]:
#         serverwatchurl=sys.argv[1]

if __name__ == "__main__":
    app.run(host = serverwatchurl, port = serverwatchport, debug = True, threaded = True)
