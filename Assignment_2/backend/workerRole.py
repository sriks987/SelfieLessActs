from pymongo import MongoClient
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

#base64 string checking
def validateandFormatTimeFormat(timestamp):
	try:
		dob= datetime.datetime.strptime(timestamp, '%d-%m-%Y:%S-%M-%H')
	except ValueError:
		# print("Incorrect Date Format. Required- YYYY-MM-DD:SS-MM-HH")
		return 0
	# print("datob:", dob)
	return 1

def validateImageFormat(ImageStr):
	try:
		print(ImageStr.encode('ascii'))
		imageB64= base64.decodestring(ImageStr.encode('ascii'))
		return 1
	except binascii.Error:
		return 0

def validatePassword(password):
	return all(c in string.hexdigits for c in password) and (len(password)==40)
# Helper functions

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

def uploadAct(actData):
		#actId = json_data['actId']
		existing_id = db.acts.find({'actId': actId}) 
		# print(existing_id)
		
		#actId should not be in db
		#int actId
		#timestamp
		#username exist
		#upvotes 0
		#categoryname must exist
		#base64
		# #category count increment

		# if existing_id == None:
		# 	# print("ID is not present")
		# 	validatResult= ValidateAndFormatTimeFormat(json_data['timestamp'])
		# 	if validatResult == 0:
		# 		return 0

		# 	# printf("Valid Time")
		# 	existing_cat= db.acts.find({'actId': actData[5]})
		# 	print(existing_cat)
		# 	if(existing_cat):
		# 		newAct= Acts(act, json_data['username']),
		# 		validatResult,json_data['caption'],json_data['imgB64'],0,json_data['categoryName']
		# 		db.session.add(newAct)
		# 		existing_cat.numberofacts+=1
		# 		db.session.commit()
		# 		return 1



		# 	else:
		# 		return 0
		# 	else:
		# 		return 0
		# 	else:
			# return 0



def deleteAct(actId):
		res = db.acts.find({'actId': actId})
		if res!=None:
			db.acts.remove({'actId': actId})
			return 1
		return 0

def check(category):
	res = category in db.list_collection_names()
	if (res == True):
	#	print("entering this.")
		acts = []
		for category1 in db[category].find():
			#print("entering this.")
			#print(category1)
			acts.append(category1)
	return acts

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

# # Relevant HTTP Response Codes: 201, 400, 405
# @app.route('/api/v1/acts', methods = ['POST', 'GET', 'DELETE', 'PUT'])
# def upload_ACT():
# 	if request.method == 'POST':
# 		actData = request.get_json(force=True)
# 		if(uploadAct(actData) == 1):
# 			return json.dumps({}), 201
# 		else:
# 			return json.dumps({}), 400
# 	else:
# 		return json.dumps({}), 405

# @app.route('/api/v1/acts/<actId>', methods = ['POST', 'GET', 'DELETE', 'PUT'])
# def delete_ACT(actId):
# 	if request.method == 'DELETE':
# 		if(deleteAct(actId) == 1):
# 			return json.dumps({}), 200
# 		else:
# 			return json.dumps({}), 400
# 	else:
# 		return json.dumps({}), 405


@app.route('/api/v1/users', methods = ["POST", "GET"])
def addUser():
	# if request.method == "GET":
	# 	return render_template("register.html")
	if request.method == "POST":
		if request.json==None:
			username = request.form.get("username")
			password = request.form.get("password")
		else:
			username = request.json["username"]
			password = request.json["password"]
		status = adduser(username, password)
		if (status == 1):
			#user created
			# msg = "New User Created. Enjoy!"
			return json.dumps({}), 201
		else:
			#user exists.
			# msg = "Please login. Your account exists."
			return json.dumps({}), 400
	else:
		return json.dumps({}), 405

@app.route('/api/v1/users/<username>', methods = ["GET", "DELETE"])
def removeUser(username):
	if request.method == 'DELETE':
		if (removeuser(username) == 1):
			return json.dumps({}), 200
		else:
			return json.dumps({}), 400
	else:
		return json.dumps({}), 405

# @app.route('/api/v1/categories/<categoryName>/acts', methods = ["GET", "DELETE", "POST", "PUT"])
# def listAllActs_category(categoryName):
# 	if request.method == "GET":
# 		res = check(categoryName)
# 		# msg = str(res)
# 		return json.dumps(res), 200
# 	else:
# 		return json.dumps({}), 405


# @app.route('/api/v1/categories/<name>/acts/size', methods = ["GET"])
# def listnumberofacts(name):
# 	from flask import jsonify
# 	if(request.method== GET):
# 		with open('categories.json') as json_file:
# 			data = json.load(json_file)
# 			return jsonify(data[name])

# @app.route('/api/v1/categories/<name>/acts?start=<startrange>&end=<endrange>',methods = ["GET"])
# def returnnumberofacts(name,startrange,endrange):
# 	from flask import jsonify
# 	if(request.method== "GET"):
# 		with open('categories.json') as json_file:
# 			data= json.load(json_file)
# 			if not data:
# 				return Response(status=204)
# 			if endrange-startrange>100:
# 				return Response(status=413)
# 			if data['Numberofacts']==0:
# 				return Response(Status=204)
# 			#get actslist from database

# 			if(len(acts_list)<startrange or len(actslist)>endrange):
# 				pass
# 			else:
# 				return jsonify(acts_list[startrange+1:endrange+2]) 

# @app.route('/api/v1/acts/upvote',methods = ["POST"])
# def upvote():
# 	json_data= request.get_json(force=True)
# 	if not json_data:
# 		print("Bad Request")
# 		return Response(status=400)
# 	else:
# 		act_id= json_data[0]
# 		req_act= Acts.query.filter_by(actID=act_id).first()
# 		if(not req_act):
# 			abort(400)
# 		print(req_act.numvotes)
# 		req_act.numvotes+=1
# 		#commit to database now. 
# 	return Response(status=200)


if __name__ == '__main__':
	app.debug == True
	app.run(host = '127.0.0.1', port = 5000)


# 201 The request has been fulfilled and has resulted in one or more new resources being created.
# 400 Bad request error
# 405 Method not allowed