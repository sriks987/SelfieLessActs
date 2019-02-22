from pymongo import MongoClient
import json
import base64
import hashlib
from flask import Flask, request, Response, abort, render_template, session, redirect, url_for, escape
app = Flask(__name__)

workerIP = '192.1234123'

# Seperate function maybe needed for logout

@app.route('/')
def login():
	#session.pop('username', None)
	return render_template("login.html", error = False)

@app.route('/valLogin', methods = ['POST'])
def valLogin():
	username = request.form.get('username')
	passwd = request.form.get('password')
	encPass = hashlib.sha1(passwd.encode('utf-8')).hexdigest()
	req =  {'username': username, 'password': encPass}
	resp = request.post(url= workerIP + '/api/v1/uservalidate', json = req)
	if(resp.status_code != 201):
		return render_template('login.html', error = True)
	else:
		session['user'] = username
		return redirect('/home')

@app.route('/home')
def homePage():
	return render_template("home.html", username = "hello")

@app.route('/upload', methods = ['POST'])
def upload():
	username = session['username']
	category = request.form.get('category')
	caption = request.form.get('caption')
	image = request.form.get('image')
	be64Img = base64.b64encode(image)
	req = {"username": username, "category": category, "caption": caption, "image": be64Img}
	resp = request.post(url = workerIP + '/api/v1/upload', json = req)
	if(resp.status_code != 201):
		return render_template('home.html', upload = True, error = True)
	else:
		return redirect('/')

@app.route('/categories', methods = ['GET'])
def categories():
	resp = request.get(url = workerIP + '/api/v1/categories')
	return render_template('categories.html', categories = resp.json())

@app.route('/catActs/<category_name>', methods = ['GET'])
def catActs(category_name):
	resp = request.get(url = workerIP + '/api/v1/acts/<category_name>')
	return render_template('acts.html', acts = resp.json())


# Remove a category
# Remove an act
if __name__ == '__main__':
	app.debug == True
	app.run(host = '127.0.0.1', port = 5005)
