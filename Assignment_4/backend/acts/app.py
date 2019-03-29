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
from flask import Flask, request, Response, abort, render_template

app = Flask(__name__)

client = MongoClient("172.17.0.2", 27017)
newIP = "http://172.17.0.3:8080"
db = client['selfie_db']

db.actRequests.insert({'requests': 0})

def checkUser(username):
	res = requests.get(url = newIP + '/api/v1/users')
	# app.logger.warning(res.json())
	res = res.json()
	if username in res:
		return 1
	else:
		return 0

def ValidateAndFormatTimeFormat(timestamp):
	try:
		dob= datetime.datetime.strptime(timestamp, '%d-%m-%Y:%S-%M-%H')
	except ValueError:
		return 0
	return 1

def is_base64(string):
	b64pattern = re.compile('^[A-Za-z0-9+\/=]+\Z')
	if len(string) % 4 == 0 and re.search(b64pattern, string)!=None:
		return 1
	else:
		return 0

def getCat():
        cursor = db.categories.find()
        res = {}
        for ele in cursor:
                res[ele['name']] = ele['count']
        return res

def insertCat(catName):
        res = db.categories.find_one({'name': catName})
        if res==None:
                db.categories.insert({"name": catName, "count": 0})
                return 1
        return 0
def delCat(catName):
        res = db.categories.find_one({'name': catName})
        if res!=None:
                db.categories.delete_one({'name': catName})
                return 1
        return 0

def getAct(category):
	res = db.acts.find( { 'categoryName': category}, {'_id':0, 'categoryName': 0 } ).count()
	if (res == 0):
		return 0
	elif (res > 100):
		return 1
	else:
		res = db.acts.find({'categoryName':category}, {'_id':0, 'categoryName':0})
		finalVal = []
		for doc in res:
			finalVal.append(doc)
		# ## app.logger.warning(finalVal)
		finalVal = sorted(finalVal, key=itemgetter('timestamp'), reverse=True)
		return finalVal

def getinAct(category, start, end):
	res = db.acts.find( { 'categoryName': category}, {'_id':0, 'categoryName': 0 } ).count()
	if (res == 0):
		return 0
	elif (start < 1):
		return 1
	elif (end > res):
		return 2
	elif (end+start-1 > 100):
		return 3
	elif (start > end):
		return 4
	elif (start > res):
		return 3
	elif (start == 1 and end == 1):
		res = db.acts.find({'categoryName':category}, {'_id':0, 'categoryName':0})
		finalValue = []
		for doc in res:
			finalValue.append(doc)
		return finalValue
	else:
		res = db.acts.find({'categoryName':category}, {'_id':0, 'categoryName':0})
		finalValue = []
		finalreturn = []
		for doc in res:
			finalValue.append(doc)
		finalValue = sorted(finalValue, key=itemgetter('timestamp'), reverse=True)
		# ## app.logger.warning(finalValue)
		for i in range(start, end):
			finalreturn.append(finalValue[i])

		return finalreturn

def length(category):
	res = db.acts.find({'categoryName':category}).count()
	return res



def uploadAct(actData):
	actId = actData['actId']
	
	if int(actId) != actId or actId < 0:
		# app.logger.warning("ACtID")
		return 0

	existing_id = db.acts.find_one({'actId': actId}) 
	if existing_id == None:
		username = actData['username']
		existing_username = checkUser(username)

		if existing_username == 0:
			# app.logger.warning("no username")
			return 0
	
		timestamp = actData['timestamp']
		validatResult= ValidateAndFormatTimeFormat(timestamp)
		if validatResult == 0:
			# app.logger.warning("time format")
			return 0
		
		caption = actData['caption']

		categoryName = actData['categoryName']
		existing_cat = db.categories.find_one({'name': categoryName})
		if existing_cat == None:
			# app.logger.warning("categoryname")
			return 0


		imgB64 = actData['imgB64']
		if is_base64(imgB64) == 0:
			# app.logger.warning("base64")
			return 0

		db.acts.insert({'actId' : actId, 'username' : username , 'timestamp' : timestamp , 'caption' : caption, 'categoryName': categoryName , 'upvote' : 0, 'imgB64' : imgB64})
		db.categories.update({'name':categoryName}, {'$inc': {'count': 1}})

		return 1
	## app.logger.warning("otherwsie")
	return 0

def deleteAct(actId):
	res = db.acts.find_one({'actId': actId})
	# ## app.logger.warning(res)
	if res != None:
		category = res['categoryName'] 
		db.acts.remove({'actId': actId})
		db.categories.update({'name':category}, {'$inc': {'count': -1}})
		return 1
	return 

def upvoteAct(actId):
	existing_act  = db.acts.find_one({'actId': actId})
	if existing_act == None:
		return 0
	db.acts.update({'actId':actId}, {'$inc': {'upvote': 1}})
	return 1

def countActs():
	res = db.acts.count()
	return res

def incrementRequests():
	db.actRequests.update( {} , {'$inc': {'requests': 1}})
	return 1

def resetRequests():
	db.actRequests.update({} , {'requests': 0})
	return 1

@app.route('/api/v1/categories/<categoryname>/acts', methods = ["GET", "PUT", "POST", "DELETE"])
def listallacts(categoryname):
	incrementRequests()
	if (request.args.get('start') is None and request.args.get('end') is None):
		if request.method == "GET":
			# app.logger.warning("6th API for: ", categoryname)
			actsGet = getAct(categoryname)
			if actsGet == 0:
				# app.logger.warning("No content for listallacts")
				return json.dumps({}),204
			elif actsGet == 1:
				# app.logger.warning("overload")
				return json.dumps({}), 413
			else:
				# app.logger.warning("Acts # app.logger.warninged")
				return json.dumps(actsGet), 200
		else:
			# app.logger.warning("Method used: ", request.method)
			return json.dumps({}), 405
	elif (len(request.args.get('start')) > 0 and len(request.args.get('end'))):
		if request.method == 'GET':
			# app.logger.warning("8th API for: ", categoryname)
			# # app.logger.warning("start: ", start)
			# # app.logger.warning("end: ", end)
			startRange=request.args.get('start',type=int)
			endRange=request.args.get('end',type=int)
			result = getinAct(categoryname, startRange, endRange)
			if (result == 0) or (result == 1):
				# app.logger.warning("Result and Start error")
				return json.dumps({}), 204
			elif (result == 2) or (result == 3) or (result == 4):
				# app.logger.warning("No Content for 8th API")
				return json.dumps({}), 204
			else:
				# app.logger.warning("# app.logger.warninged Successfully")
				return json.dumps(result), 200
		else:
			# app.logger.warning("Method Used: ", request.method)
			return json.dumps({}), 405

@app.route('/api/v1/categories', methods = ['POST', 'GET', 'DELETE', 'PUT'])
def listCat():
	incrementRequests()
	if request.method == 'GET':
		catCount = getCat()
		if len(catCount)>0:
			# app.logger.warning("All Categories # app.logger.warninged")
			return json.dumps(catCount), 200
		else:
			# app.logger.warning("No Categories to # app.logger.warning")
			return json.dumps({}), 204

	elif request.method == 'POST':
		catData = request.get_json(force=True)
		if(insertCat(catData[0])==1):
			# app.logger.warning(catData[0], "was Successfully inserted")
			return json.dumps({}), 201
		else:
			# app.logger.warning("Bad Request Error for listing Categories")
			return json.dumps({}), 400
	else:
		# app.logger.warning("Method Used: ", request.method)
		return json.dumps({}), 405

@app.route('/api/v1/categories/<category_name>', methods = ['POST', 'GET', 'DELETE', 'PUT'])
def removeCategory(category_name):
	incrementRequests()
	if request.method == 'DELETE':
		# app.logger.warning("Deleting: ", category_name)
		if(delCat(category_name)==1):
			# app.logger.warning("Success")
			return json.dumps({}), 200
		else:
			# app.logger.warning("No Category to delete")
			return json.dumps({}), 400
	else:
		# app.logger.warning("Method Used: ", request.method)
		return json.dumps({}), 405

@app.route('/api/v1/categories/<categoryname>/acts/size', methods = ["POST", "PUT", "GET", "DELETE"])
def listnumberofacts(categoryname):
	incrementRequests()
	if request.method == "GET":
		# app.logger.warning(categoryname, " asked")
		count = length(categoryname)
		if (count > 0):
			# app.logger.warning("Size of ", categoryname, ":", count)
			return json.dumps(count), 200
		else:
			# app.logger.warning("No content for: ", categoryname)
			return json.dumps({}), 204
	else:
		# app.logger.warning("Method Used: ", request.method)
		return json.dumps({}), 405

@app.route('/api/v1/acts', methods = ['POST', 'GET', 'DELETE', 'PUT'])
def upload_ACT():
	incrementRequests()
	# app.logger.warning("Upload Act")
	if request.method == 'POST':
		# app.logger.warning("Method Used: POST")
		actData = request.get_json(force=True)
		checking = []
		for key in actData:
			checking.append(key)
		arraytocheck = ["username", "timestamp", "categoryName", "imgB64", "caption", "actId"]
		if (arraytocheck == checking):
			# app.logger.warning("Error in Checking.")
			return json.dumps({}), 400
		elif(uploadAct(actData) == 1):
			# app.logger.warning("Uploaded Act")
			return json.dumps({}), 201
		else:
			# app.logger.warning("Else Error")
			return json.dumps({}), 400
	else:
		# app.logger.warning("Method Used: ", request.method)
		return json.dumps({}), 405
@app.route('/api/v1/acts/<actId>', methods = ['POST', 'GET', 'DELETE', 'PUT'])
def delete_ACT(actId):
	incrementRequests()
	# app.logger.warning("Delete Act")
	actId = int(actId)
	if request.method == 'DELETE':
		# app.logger.warning("ActID: ", actId)
		if(deleteAct(actId) == 1):
			# app.logger.warning("ActID present and deleted")
			return json.dumps({}), 200
		else:
			# app.logger.warning("ActID not present")
			return json.dumps({}), 400
	else:
		# app.logger.warning("Method Used: ", request.method)
		return json.dumps({}), 405

@app.route('/api/v1/acts/upvote',methods = ['POST', 'PUT', 'DELETE', 'GET'])
def upvote():
	incrementRequests()
	# app.logger.warning("Upvote Act.")
	if request.method == "POST":
		upvoteID = request.get_json(force=True)
		# app.logger.warning("ActID: ", upvoteID[0])
		if(upvoteAct(upvoteID[0])==1):
			# app.logger.warning("Act Upvoted.")
			return json.dumps({}), 200
		else:
			# app.logger.warning("Not present.")
			return json.dumps({}), 400
	else:
		# app.logger.warning("Method Used: ", request.method)
		return json.dumps({}), 405

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
	if request.method == "GET":
		res = countActs()
		return json.dumps([res]), 200
	else:
		return json.dumps({}), 405

if __name__ == '__main__':
	app.debug == True
	app.run(host='0.0.0.0', port=80, debug = True)
