from eve import Eve
from eve_docs import eve_docs
from flask import send_from_directory
import sys
# import socket



import logging
#from eve.auth import BasicAuth

# To use this basic auth just pass the className of Authentication class in EVE() constructor call below.
from flask_bootstrap import Bootstrap

#gestion adresse serveur API
# hostname = socket.gethostname()
# IPAddr = socket.gethostbyname_ex(hostname)
listenURL="127.0.0.1"

"""
class MyBasicAuth(BasicAuth):
    def check_auth(self, username, password, allowed_roles, resource, method):
        return username == 'admin' and password == 'secret'
"""

# FUNCTION FOR ADDING MORE FUNCTIONALITY WHEN RETURNING THE DATA
def piterpy(response):
    for document in response['_items']:
        document['PITERPY'] = 'New Field'

def before_returning_items(resource_name, response):
    print('About to return items from "%s" ' % resource_name)

app = Eve()
#app.on_fetched_resource += piterpy
#app.on_fetched_resource += before_returning_items

#app.on_fetched_resource_factory += piterpy

#app.config['SERVER_NAME'] = "10.190.76.64:5000" # as this is the value that is replaced in the docs TEMPLATE. (use IP address)
app.config['API_NAME'] = "Factory of the Future - List of End-Points" # as this is the value that is replaced in the docs TEMPLATE.

# define custom routes
@app.route('/fof')
def fof():
    return 'The API is working<br />This is a custom road for the Factory of the Future API'
@app.route('/favicon.ico')
def favicon():
    # return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    try:
        val = __file__.rindex('\\')
    except ValueError:
        val = __file__.rindex('/')
    return send_from_directory(__file__[:val], 'favicon.ico', mimetype='image/vnd.microsoft.icon')

Bootstrap(app)
app.register_blueprint(eve_docs, url_prefix='/docs')  # can change the URL if you want.
if len(sys.argv) > 1:
    # need argument in order to run for any computer on network
    print('run with 1st argument listen API url',sys.argv[1])
    if not False in [c in "0123456789." for c in sys.argv[1]]:
        listenURL = sys.argv[1]
    else:
        print("need IP adresse")
        exit()

print("listen on " + listenURL)    
app.run(host = listenURL, port = 5000, debug = True, threaded = True)
