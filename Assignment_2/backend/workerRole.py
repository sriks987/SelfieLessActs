from operator import itemgetter
from pymongo import MongoClient
import re
import json
import base64
import string
import binascii
import datetime
import hashlib
from flask import Flask, request, Response, abort, render_template

app = Flask(__name__)

client = MongoClient()
db = client['selfie_db']

#Helper Functions

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
		

def validatePassword(password):
	return all(c in string.hexdigits for c in password) and (len(password)==40)

def adduser(username, password):
	if (validatePassword(password)==True):
		res = db.users.find_one({'name': username})
		if res==None:	
			db.users.insert({"name": username, "password": password})
			return 1
		else:
			return 0
	else:
		return 0

def removeuser(username):
	res = db.users.find_one({'name': username})
	if res != None:
		db.users.delete_one({'name' : username})

		return 1
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
		# #print(finalVal)
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
		# #print(finalValue)
		for i in range(start, end):
			finalreturn.append(finalValue[i])

		return finalreturn


def length(category):
	res = db.acts.find({'categoryName':category}).count()
	return res



def uploadAct(actData):
	actId = actData['actId']
	# if actId.isdigit() == False:
		# return 0
	if int(actId) != actId or actId < 0:
		#print("error here")
		return 0

	existing_id = db.acts.find_one({'actId': actId}) 
	if existing_id == None:
		username = actData['username']
		existing_username = db.users.find_one({'name' : username})
		if existing_username == None:
			#print("heree")
			return 0
	
		timestamp = actData['timestamp']
		validatResult= ValidateAndFormatTimeFormat(timestamp)
		if validatResult == 0:
			#print("validate")
			return 0
		
		caption = actData['caption']

		categoryName = actData['categoryName']
		existing_cat = db.categories.find_one({'name': categoryName})
		if existing_cat == None:
			#print("categoryname")
			return 0


		imgB64 = actData['imgB64']
		if is_base64(imgB64) == 0:
			#print("base64")
			return 0

		db.acts.insert({'actId' : actId, 'username' : username , 'timestamp' : timestamp , 'caption' : caption, 'categoryName': categoryName , 'upvote' : 0, 'imgB64' : imgB64})
		db.categories.update({'name':categoryName}, {'$inc': {'count': 1}})

		return 1
	#print("otherwsie")
	return 0


def deleteAct(actId):
	res = db.acts.find_one({'actId': actId})
	# #print(res)
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

def getPassword(username):
	res = db.users.find_one({'name': username})
	if res==None:
		return None
	else:
		return res['password']

@app.route('/api/v1/valLogin', methods = ["POST"])
def valLogin():
	if request.method == "POST":
		username = request.json["username"]
		password = request.json["password"]
		realPass = getPassword(username)
		if realPass is not None:
			if password == realPass:
				return json.dumps({}), 201
			else:
				return json.dumps({}), 400
		else:
			return json.dumps({}), 400
	else:
		return json.dumps({}), 405

@app.route('/api/v1/getNum', methods = ["GET"])
def getNum():
	actNum = db.acts.count()
	return json.dumps({'actID': actNum + 1}),200



@app.route('/api/v1/users', methods = ["POST", "GET", "DELETE", "PUT"])
def addUser():
	if request.method == "POST":
		if request.json==None:
			username = request.form.get("username")
			password = request.form.get("password")
		else:
			username_password = request.get_json(force=True)
			newset = []
			for key in username_password:
				newset.append(key)
			# #print(newset[0] + " " + newset[1])
			if (newset[0] != "username" or newset[1] != "password"):
				# #print("here")
				return json.dumps({}), 400
			else:	
				# #print("otherwise")
				username = request.json["username"]
				password = request.json["password"]
				status = adduser(username, password)
				if (status == 1):
					return json.dumps({}), 201
				else:
					return json.dumps({}), 400
	else:
		return json.dumps({}), 405

@app.route('/api/v1/users/<username>', methods = ["GET", "DELETE", "POST", "PUT"])
def removeUser(username):
	if request.method == 'DELETE':
		if (removeuser(username) == 1):
			return json.dumps({}), 200
		else:
			return json.dumps({}), 400
	else:
		return json.dumps({}), 405

@app.route('/api/v1/categories/<categoryname>/acts', methods = ["GET", "PUT", "POST", "DELETE"])
def listallacts(categoryname):
	if (request.args.get('start') is None and request.args.get('end') is None):
		if request.method == "GET":
			#print("all")
			actsGet = getAct(categoryname)
			if actsGet == 0:
				return json.dumps({}),204
			elif actsGet == 1:
				return json.dumps({}), 413
			else:
				return json.dumps(actsGet), 200
		else:
			return json.dumps({}), 405
	elif (len(request.args.get('start')) > 0 and len(request.args.get('end'))):
		if request.method == 'GET':
			startRange=request.args.get('start',type=int)
			endRange=request.args.get('end',type=int)
			#print("Coming from Listing in Range")
			result = getinAct(categoryname, startRange, endRange)
			if (result == 0) or (result == 1):
				return json.dumps({}), 204
			elif (result == 2) or (result == 3) or (result == 4):
				return json.dumps({}), 204
			else:
				return json.dumps(result), 200
		else:
			return json.dumps({}), 405

@app.route('/api/v1/categories', methods = ['POST', 'GET', 'DELETE', 'PUT'])
def listCat():
	if request.method == 'GET':
		catCount = getCat()
		if len(catCount)>0:
			return json.dumps(catCount), 200
		else:
			return json.dumps({}), 204

	elif request.method == 'POST':
		catData = request.get_json(force=True)
		if(insertCat(catData[0])==1):
			return json.dumps({}), 201
		else:
			return json.dumps({}), 400
	else:
		return json.dumps({}), 405
        
@app.route('/api/v1/categories/<category_name>', methods = ['POST', 'GET', 'DELETE', 'PUT'])
def removeCategory(category_name):
	if request.method == 'DELETE':
		if(delCat(category_name)==1):
			return json.dumps({}), 200
		else:
			return json.dumps({}), 400
	else:
		return json.dumps({}), 405

@app.route('/api/v1/categories/<categoryname>/acts/size', methods = ["POST", "PUT", "GET", "DELETE"])
def listnumberofacts(categoryname):
	if request.method == "GET":
		count = length(categoryname)
		if (count > 0):
			return json.dumps(count), 200
		else:
			return json.dumps({}), 204
	else:
		return json.dumps({}), 405

@app.route('/api/v1/acts', methods = ['POST', 'GET', 'DELETE', 'PUT'])
def upload_ACT():
	if request.method == 'POST':
		actData = request.get_json(force=True)
		checking = []
		for key in actData:
			checking.append(key)
		# #print(checking)
		if (checking[0] != 'actId' or checking[1] != 'username' or checking[2] != 'timestamp' or checking[3] != 'caption' or checking[4] != 'categoryName' or checking[5] != 'imgB64'):
			#print(checking)
			return json.dumps({}), 400
		elif(uploadAct(actData) == 1):
			return json.dumps({}), 201
		else:
			#print("here")
			return json.dumps({}), 400
	else:
		return json.dumps({}), 405


@app.route('/api/v1/acts/<actId>', methods = ['POST', 'GET', 'DELETE', 'PUT'])
def delete_ACT(actId):
	actId = int(actId)
	if request.method == 'DELETE':
		if(deleteAct(actId) == 1):
			return json.dumps({}), 200
		else:
			return json.dumps({}), 400
	else:
		return json.dumps({}), 405

@app.route('/api/v1/acts/upvote',methods = ["POST", "PUT", "DELETE", "GET"])
def upvote():
	if request.method == "POST":
		upvoteID = request.get_json(force=True)
		print(upvoteID)
		if(upvoteAct(int(upvoteID[0]))==1):
			return json.dumps({}), 200
		else:
			return json.dumps({}), 400
	else:
		return json.dumps({}), 405


if __name__ == '__main__':
	app.debug == True
	app.run(host='0.0.0.0', port=5000, debug = True)

