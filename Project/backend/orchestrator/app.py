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

client = MongoClient("172.17.0.2", 27017)
newIP = "http://172.17.0.3:8080"
db = client['selfie_db']

portLists = []
index = 0

db.actRequests.insert({'requests': 0})

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


if __name__ == '__main__':
	app.debug == True
	app.run(host='0.0.0.0', port=80, debug = True)
