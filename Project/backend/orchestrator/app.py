from flask import Flask, request, Response, abort, render_template
import os
import requests
import time
import math
from threading import Thread, Lock
import subprocess, signal
import logging
from time import sleep
import json

app = Flask(__name__)
portList = []
index = 0
lock = Lock()
incCount = Lock()
requestCount = 0
with open('config.json') as json_file:
	f = json_file.read()
	data = json.loads(f)


@app.route(data["baseUrl"]+"<path:remaining>", methods=["GET", "POST", "PUT", "DELETE"])
def balance(remaining):
	global index
	global requestCount
	incCount.acquire()
	requestCount = requestCount + 1
	incCount.release()

	lock.acquire()
	if index>=len(portList):
		index = 0
	currPort = portList[index]
	lock.release()

	if request.method == 'GET':
		var = requests.get(url="http://localhost:"+str(currPort) + "/api/v1/"+remaining)
		app.logger.warning(type(var.status_code))
		if (var.status_code == 204):
			r1 = {}
		else:
			r1 = var.json()
	elif request.method == 'POST':
		jsonPart = request.get_json()
		var = requests.post(url = 'http://localhost:' + str(currPort) + '/api/v1/' + remaining, json = jsonPart)
		r1 = var.json()
	elif request.method == 'PUT':
		jsonPart = request.get_json()
		var = requests.put(url = 'http://localhost:' + str(currPort) + '/api/v1/' + remaining, json = jsonPart)
		r1 = var.json()
	elif request.method == 'DELETE':
		jsonPart = request.get_json()
		var = requests.delete(url = 'http://localhost:' + str(currPort) + '/api/v1/' + remaining, json = jsonPart)
		r1 = var.json()
	app.logger.warning(portList[index])
	lock.acquire()
	index = (index + 1)%(len(portList))
	lock.release()
	return json.dumps(r1), var.status_code


def scaling():
	global requestCount
	while requestCount==0:
		pass
	while True:
		sleep(data['timeBetweenScaling'])
		var = requestCount
		diff = var//20 - len(portList) + 1
		app.logger.warning(diff)
		if diff > 0:
			for i in range(0, diff):
				lock.acquire()
				port = portList[-1]+1
				lock.release()
				os.system('docker run -d -p '+ str(port) + ':80 acts')
				portList.append(port)
				app.logger.warning("adding")

		else:
			for i in range(0, abs(diff)):
				lock.acquire()
				port = portList.pop()
				lock.release()
				os.system('docker rm $(docker ps -a | grep "'+str(port)+'") --force')
				app.logger.warning("removing")
				app.logger.warning(port)
		incCount.acquire()
		requestCount = 0
		incCount.release()
scaling_thread = Thread(target=scaling)
scaling_thread.start()


def initializeContainer():
	os.system("docker run -d -p"+str(data['initialPort'])+":80 "+data['dockerFile'])
	portList.append(data['initialPort'])

initializeContainer()

def monitorHealth():
	sleep(5)
	while True:
	# app.logger.warning(len(portList))
		for i in range(0, len(portList)):
			res = requests.get(url='http://localhost:'+str(portList[i])+'/api/v1/_health')
			if res.status_code == 500:
				app.logger.warning("crashed container")
				app.logger.warning(portList[i])
				lock.acquire()
				temp = portList[i]
				del portList[i]
				lock.release()
				os.system('docker rm $(docker ps -a | grep "'+str(temp)+'->80") --force')
				os.system('docker run -d -p'+str(temp)+':80 acts')
				lock.acquire()
				portList.append(temp)
				portList.sort()
				lock.release()
				
		sleep(data['healthCheck'])
healthcheck_thread = Thread(target=monitorHealth)
healthcheck_thread.start()



def loadBalancer():
	app.run(host='0.0.0.0', port=80)

loadBalancerthread = Thread(target=loadBalancer)
loadBalancerthread.start()