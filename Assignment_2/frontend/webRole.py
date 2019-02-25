from pymongo import MongoClient
import json
import base64
import requests
import hashlib
from datetime import datetime
from flask import Flask, request, Response, abort, render_template, session, redirect, url_for, escape
app = Flask(__name__)
app.secret_key = 'super secret key'

workerIP = 'http://0.0.0.0:5000'

# Seperate function maybe needed for logout

@app.route('/')
def login():
	#if 'username' in session:
	#	session.pop('username', None)
	return render_template("login.html", error = False)

@app.route('/register')
def register():
	return render_template("register.html", error = False)

@app.route('/addUserFront', methods = ['POST'])
def addUserFront():
	username = request.form.get('username')
	passwd = request.form.get('password')
	encPass = hashlib.sha1(passwd.encode('utf-8')).hexdigest()
	req = {'username': username, 'password':encPass}
	resp = requests.post(url = workerIP + '/api/v1/users', json = req)
	if(resp.status_code != 201):
		return render_template('register.html', error = True)
	else:
		return redirect('/home')

@app.route('/valLoginFront', methods = ['POST'])
def valLoginFront():
	username = request.form.get('username')
	passwd = request.form.get('password')
	encPass = hashlib.sha1(passwd.encode('utf-8')).hexdigest()
	req =  {'username': username, 'password': encPass}
	resp = requests.post(url= workerIP + '/api/v1/valLogin', json = req)
	if(resp.status_code != 201):
		return render_template('login.html', error = True)
	else:
		session['username'] = username
		return redirect('/home')

@app.route('/home')
def homePage():
	return render_template("home.html", username = session['username'])

@app.route('/uploadFront', methods = ['POST'])
def uploadFront():
	username = session['username']
	category = request.form.get('category')
	caption = request.form.get('caption')
	image = request.files['file'].read()
	be64Img = base64.b64encode(image).decode("utf-8")
	resp = requests.get(url = workerIP + '/api/v1/getNum')
	newID = resp.json()
	actID = newID['actID']
	now = datetime.now()
	timeStp = now.strftime("%d-%m-%Y:%S-%M-%H")
	req = {"actId": actID, "username": username, "timestamp": timeStp, "caption": caption, "categoryName": category, "imgB64": be64Img}
	resp = requests.post(url = workerIP + '/api/v1/acts', json = req)
	if(resp.status_code != 201):
		return render_template('home.html', upload = True, error = True)
	else:
		return redirect('/home')

@app.route('/upvoteActFront', methods = ['POST'])
def upvoteActFront():
	actID = request.form.get('submit')
	print(actID)
	print(type(actID))
	req = [actID]
	resp = requests.post(url = workerIP + '/api/v1/acts/upvote', json = req)
	return redirect('/home')
	# Make request to upvote the act

@app.route('/deleteActFront')
def deleteActFront():
	actID = request.form.get('submit')
	resp = requests.delete(url = workerIP + '/api/v1/acts/' + actID)
	return redirect('/home')
	# Make request to delete the act

@app.route('/deleteCatFront')
def deleteCatFront():
	catName = request.form.get('submit')
	resp = requests.delete(url = workerIP + '/api/v1/categories/' + catName)
	return redirect('/home')

@app.route('/categoriesFront')
def categoriesFront():
	resp = requests.get(url = workerIP + '/api/v1/categories')
	return render_template('categories.html', categories = resp.json())

@app.route('/catActs', methods = ['POST'])
def catActs():
	category_name = request.form.get('category_name')
	resp = requests.get(url = workerIP + '/api/v1/categories/' + category_name + '/acts' )
	return render_template('acts.html', acts = resp.json())


# Remove a category
# Remove an act
if __name__ == '__main__':
	
	app.config['SESSION_TYPE'] = 'filesystem'

	app.debug = True
	app.run(host = '127.0.0.1', port = 5005)
