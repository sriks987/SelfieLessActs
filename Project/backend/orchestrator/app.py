import os
import logging
import json
import requests
from time import sleep
import threading
from werkzeug.routing import Map, Rule, NotFound, RequestRedirect
from flask import Flask, request, Response, abort, render_template

app = Flask(__name__)
portList = []
index = 0
startFlag = 0

@app.route("/api/v1/<path:remaining>", methods=["GET", "POST", "PUT", "DELETE"])
def balance(remaining):
	global startFlag
	if startFlag == 0:
		scaling_thread.start()
		startFlag = 1
	global index
	app.logger.warning(remaining)
	if request.method == 'GET':
		var = str(requests.get(url = 'http://127.0.0.1:' + str(portList[index]) + '/api/v1/' + remaining).json())
	elif request.method == 'POST':
		jsonPart = request.get_json()
		var = str(requests.post(url = 'http://127.0.0.1:' + str(portList[index]) + '/api/v1/' + remaining, json = jsonPart).json())
	elif request.method == 'PUT':
		jsonPart = request.get_json()
		var = str(requests.put(url = 'http://127.0.0.1:' + str(portList[index]) + '/api/v1/' + remaining, json = jsonPart).json())
	elif request.method == 'DELETE':
		jsonPart = request.get_json()
		var = str(requests.delete(url = 'http://127.0.0.1:' + str(portList[index]) + '/api/v1/' + remaining, json = jsonPart).json())
	app.logger.warning(portList[index])
	index = (index + 1)%(len(portList))
	return var

def scaling():
	while True:
		var = requests.get("http://localhost:8000/api/v1/_count").json()
		app.logger.warning(var[0])
		if var[0]//20 == len(portList) or len(portList) == 1:
			continue
		else:
			diff = var[0]//20 - len(portList)
			app.logger.warning(diff)
			if diff > 0:
				for i in range(0, diff):
					port = portList[-1]+1
					portList.append(port)
					os.system('docker run -d -p '+ str(port) + ':80 acts')
			else:
				for i in range(0, abs(diff)):
					port = portList.pop()
					os.system('docker rm $(docker ps -a | grep "'+str(port)+'->80/tcp" --force')
		sleep(40)

def monitorHealth():
	while True:
		for i in range(len(portList)):
			portNumber = portList[i]
			res = requests.get(url = 'http://localhost:' + str(portNumber) + '/api/v1/_health')
			if res.status_code == 500:
				os.system('docker rm $(docker ps -a | grep "'+str(portNumber)+'>80/tcp" --force')
				os.system('docker run -d -p ' + str(portNumber) + ':80 acts')
		sleep(1)


def callBalance():
	app.run(host='0.0.0.0', port=80)

#threads = []
scaling_thread = threading.Thread(target=scaling)
healthcheck_thread = threading.Thread(target=monitorHealth)
app = threading.Thread(target=callBalance)


app.start()

def initializeContainer():
	os.system("docker run -d -p 8000:80 acts")
	portList.append(8000)

initializeContainer()

if __name__ == '__main__':
	
	scaling_thread.start()
	healthcheck_thread.start()

	# don't join because it is a infinite loop
	# need to keep running indefinitely.

	
