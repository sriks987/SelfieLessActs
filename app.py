import logging
from operator import itemgetter
from pymongo import MongoClient
import re
import json
import requests
import base64
import string
import binascii
import datetime
import hashlib
import threading
from werkzeug.routing import Map, Rule, NotFound, RequestRedirect
from flask import Flask, request, Response, abort, render_template

app = Flask(__name__)
portLists = [8000]
index = 0

#global thread creation
#balance_thread = threading.Thread(target=balance)
scaling_thread = threading.Thread(target=scaling)
healthcheck_thread = threading.Thread(target=monitorHealth)


@app.route("/api/v1/<path:remaining>", methods=["GET", "POST", "PUT", "DELETE"])
def balance(remaining):
	global index
	app.logger.warning(remaining)
	if request.method == 'GET':
		var = str(requests.get(url = 'http://127.0.0.1:' + str(portLists[index]) + '/api/v1/' + remaining).json())
	elif request.method == 'POST':
		jsonPart = request.get_json()
		var = str(requests.post(url = 'http://127.0.0.1:' + str(portLists[index]) + '/api/v1/' + remaining, json = jsonPart).json())
	elif request.method == 'PUT':
		jsonPart = request.get_json()
		var = str(requests.put(url = 'http://127.0.0.1:' + str(portLists[index]) + '/api/v1/' + remaining, json = jsonPart).json())
	elif request.method == 'DELETE':
		jsonPart = request.get_json()
		var = str(requests.delete(url = 'http://127.0.0.1:' + str(portLists[index]) + '/api/v1/' + remaining, json = jsonPart).json())
	app.logger.warning(portLists[index])
	index = (index + 1)%(len(portLists))
	return var

def scaling():
        while True:
                var = requests.get("http://localhost:8000/api/v1/_count").json()
                if var[0]/20 == len(portLists):
                        continue
                else:
                        diff = var[0]//20 - len(portLists)
                        if diff > 0:
                                for i in range(0, diff):
                                        port = portLists[-1]+1
                                        portLists.append(port)
                                        os.execute('docker run -d -p '+ str(port) + ':80 acts')
                        else:
                                for i in range(0, math.abs(diff)):
                                        port = portLists.pop()
                                        os.execute('docker rm $(docker ps -a | grep "'+str(port)+'>80/tcp" --force')
                sleep(40)

def monitorHealth():
    while True:
        for i in range(len(portList)):
                portNumber = portList[i]
                res = requests.get(url = 'http://localhost:' + str(portNumber) + '/api/v1/_health')
                if res.status_code == 500:
                        os.execute('docker rm $(docker ps -a | grep "'+str(portNumber)+'>80/tcp" --force')
                        os.execute('docker run -d -p ' + str(portNumber) + ':80 acts')
        sleep(1)



#threads = []

if __name__ == '__main__':
	
    #balance_thread.start()
    scaling_thread.start()
    healthcheck_thread.start()

    #for t in threads:
    #    t.join()
    
    #balance_thread.join()
    scaling_thread.join()
    healthcheck_thread.join()

    app.debug == True
    app.run(host='0.0.0.0', port=80, debug = True)
