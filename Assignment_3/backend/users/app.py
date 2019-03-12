import logging
import json
from flask import Flask, request
from pymongo import MongoClient
import string

app = Flask(__name__)
client = MongoClient("172.17.0.2", 27017)
db = client["selfie_db"]

def validatePassword(password):
	return all(c in string.hexdigits for c in password) and (len(password) == 40)

def adduser(username, password):
	if (validatePassword(password) ==  True):
		res = db.users.find_one({'name': username})
		if res == None:
			db.users.insert({"name":username, "password":password})
			return 1
		else:
			return 2
	else:
		return 0

def removeuser(username):
	res = db.users.find_one({"name": username})
	if res != None:
		db.users.delete_one({"name": username})
		return 1
	else:
		return 0

def listAllUsers():
	res = db.users.find({}, {'_id': 0, 'password': 0})
	if res == None:
		return 0
	else:
		users = []
		for doc in res:
			users.append(doc['name'])
		if users == []:
			return 0
		else:
			return users

@app.route("/api/v1/users", methods = ["POST", "GET", "DELETE", "PUT"])
def addUser():
	if request.method == "GET":
		res = listAllUsers()
		if res != 0:
			# app.logger.warning("users listed")
			return (json.dumps(res)), 200
		else:
			# app.logger.warning("no content")
			return json.dumps({}), 204
	elif request.method == "POST":
		username_password = request.get_json(force=True)
		newset = []
		for key in username_password:
			 newset.append(key)
		newarray = ["username", "password"]
		newset.sort()
		newarray.sort()
		if (newarray != newset):
			# app.logger.warning("wrong format")
			return json.dumps({}), 400
		else:
			username = request.json["username"]
			password = request.json["password"]
			status = adduser(username, password)
			if (status == 1):
				# app.logger.warning("created user")
				return json.dumps({}), 201
			elif (status == 2):
				# app.logger.warning("not created", username)
				return json.dumps({}), 400
			else:
				# app.logger.warning("not created", username)
				return json.dumps({}), 400
	else:
		# app.logger.warning("wrong method used")
		return json.dumps({}), 405

@app.route("/api/v1/users/<username>", methods=["POST", "GET", "PUT", "DELETE"])
def removeUser(username):
	if request.method == "DELETE":
		res = removeuser(username)
		if (res == 1):
			# app.logger.warning("User deleted")
			return json.dumps({}), 200
		else:
			# app.logger.warning("Not deleted", username)
			return json.dumps({}), 400
	else:
		# app.logger.warning("Wrong Method Used")
		return json.dumps({}), 405


if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port = 8080, debug = True)
