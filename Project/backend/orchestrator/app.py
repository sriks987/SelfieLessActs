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

db.actRequests.insert({'requests': 0})

healthyContainers = []
unhealthyContainers = []

def incrementRequests():
	db.actRequests.update( {} , {'$inc': {'requests': 1}})
	return 1

def resetRequests():
	db.actRequests.update({} , {'requests': 0})
	return 1
'''
@app.route('/api/v1/categories/<categoryname>/acts', methods = ["GET", "PUT", "POST", "DELETE"])
def listallacts(categoryname):
	incrementRequests()
	

@app.route('/api/v1/categories', methods = ['POST', 'GET', 'DELETE', 'PUT'])
def listCat():
	incrementRequests()
	

@app.route('/api/v1/categories/<category_name>', methods = ['POST', 'GET', 'DELETE', 'PUT'])
def removeCategory(category_name):
	incrementRequests()
	
@app.route('/api/v1/categories/<categoryname>/acts/size', methods = ["POST", "PUT", "GET", "DELETE"])
def listnumberofacts(categoryname):
	incrementRequests()
	
@app.route('/api/v1/acts', methods = ['POST', 'GET', 'DELETE', 'PUT'])
def upload_ACT():
	incrementRequests()
	
@app.route('/api/v1/acts/<actId>', methods = ['POST', 'GET', 'DELETE', 'PUT'])
def delete_ACT(actId):
	incrementRequests()
	
@app.route('/api/v1/acts/upvote',methods = ['POST', 'PUT', 'DELETE', 'GET'])
def upvote():
	incrementRequests()
	
@app.route('/api/v1/_count', methods = ['GET', 'DELETE', 'POST', 'PUT'])
def countAPI():
	# To return the number of request made
	#incrementRequests()
	if request.method == 'GET':
		res = db.actRequests.find_one({}, {'requests': 1})
		return json.dumps([res]),  200
	elif request.method == 'DELETE':
		resetRequests()
		return json.dumps({}), 200
	else:
		return json.dumps({}), 405

@app.route('/api/v1/acts/count', methods = ['GET', 'DELETE', 'POST', 'PUT'])
def count():
	incrementRequests()
	
@app.route('/api/v1/_health', methods = ['GET'])
def health():
	return '', 500

@app.route('/api/v1/_crash', methods = ['POST'])
def crash():
	return '', 200



@app.route('/api/v1/', methods = ['GET', 'DELETE', 'POST', 'PUT'])
def balance():
    if 
'''
'''
def healthCheck():
    res = requests.get(localhost + healthyContainers[0] + '/api/v1/_health')
'''

'''
def scale():
    if countRequests
'''


if __name__ == '__main__':
	app.debug == True
	app.run(host='0.0.0.0', port=80, debug = True)
