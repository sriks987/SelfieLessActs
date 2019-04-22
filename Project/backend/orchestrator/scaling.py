import os
from time import sleep
from flask import *
import requests

portLists = [8001]
index  = 0

while True:
        global index
        var = requests.get("http://localhost:8001/api/v1/_count").json()
        if var[0]/20 == len(portLists):
                continue
        else:
#               lastPort = portLists[-1+1]
                for i in range(0, (var[0]//20)-len(portLists)):
                        port = portLists[-1]+1
                        portLists.append(port)
                        os.execute('docker run -d -p '+ str(port) + ':80 acts')

        sleep(40)

@app.route("/api/v1/categories")
def fun():
        res = requests.get('http://localhost:8001/api/v1/categories')
        return str(res.json())

if __name__ == '__main__':
        app.run(host='0.0.0.0', port=80)

