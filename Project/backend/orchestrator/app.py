from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from flask import json
import os
import requests
import time
import math
from threading import Thread, Lock
import subprocess, signal
import logging
from time import sleep

app = Flask(__name__)
portList = []
index = 0
lock= Lock()
healthlock = Lock()
incCount = Lock()
requestCount = 0


@app.route("/api/v1/<path:remaining>", methods=["GET", "POST", "PUT", "DELETE"])
def balance(remaining):
	global index
	global requestCount
	app.logger.warning(remaining)
	if request.method == 'GET':
		var = requests.get(url="http://3.212.219.92:"+str(portList[index]) + "/api/v1/"+remaining)
		r1 = var.json()
		incCount.acquire()
		requestCount = requestCount + 1
		incCount.release()
	elif request.method == 'POST':
		jsonPart = request.get_json()
		var = requests.post(url = 'http://3.212.219.92:' + str(portList[index]) + '/api/v1/' + remaining, json = jsonPart)
		r1 = var.json()
		incCount.acquire()
		requestCount = requestCount + 1
		incCount.release()
	elif request.method == 'PUT':
		jsonPart = request.get_json()
		var = requests.put(url = 'http://3.212.219.92:' + str(portList[index]) + '/api/v1/' + remaining, json = jsonPart)
		r1 = var.json()
		incCount.acquire()
		requestCount = requestCount + 1
		incCount.release()
	elif request.method == 'DELETE':
		jsonPart = request.get_json()
		var = requests.delete(url = 'http://3.212.219.92:' + str(portList[index]) + '/api/v1/' + remaining, json = jsonPart)
		r1 = var.json()
		incCount.acquire()
		requestCount = requestCount + 1
		incCount.release()

	app.logger.warning(portList[index])
	index = (index + 1)%(len(portList))
	return json.jsonify(r1), var.status_code

def scaling():
	global requestCount
	while requestCount==0:
		  pass
	while True:
		var = requestCount
		if var//20 == len(portList) or len(portList) == 1:
			continue
		else:
			diff = var//20 - len(portList)
			app.logger.warning(diff)
			if diff > 0:
				for i in range(0, diff):
					lock.acquire()
					port = portList[-1]+1
					portList.append(port)
					os.system('docker run -d -p '+ str(port) + ':80 acts')
					lock.release()
			else:
				for i in range(0, abs(diff)):
					port = portList.pop()
					os.system('docker rm $(docker ps -a | grep "'+str(port)+'->80/tcp" --force')
		sleep(120)
	requestCount = 0

scaling_thread = Thread(target=scaling)

def monitorHealth():
	while True:
		for i in range(len(portList)):
			healthlock.acquire()
			portNumber = portList[i]
			res = requests.get(url = 'http://localhost:' + str(portNumber) + '/api/v1/_health')
			if res.status_code == 500:
				os.system('docker rm $(docker ps -a | grep "'+str(portNumber)+'>80/tcp" --force')
				os.system('docker run -d -p ' + str(portNumber) + ':80 acts')
			healthlock.release()
		sleep(1)
healthcheck_thread = Thread(target=monitorHealth)
healthcheck_thread.start()

def callBalance():
	#app.debug == True
	app.run(host='0.0.0.0', port=80)

appnew = Thread(target=callBalance)

def initializeContainer():
	os.system("docker run -d -p 8000:80 acts")
	portList.append(8000)

initializeContainer()

if __name__ == '__main__':
	appnew.start()
	scaling_thread.start()
	logging.debug("Done")
