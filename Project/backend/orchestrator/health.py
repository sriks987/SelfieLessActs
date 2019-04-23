import os
from time import sleep
from flask import *
import requests

portList= []

def monitorHealth():
    while True:
        for i in range(len(portList)):
            res = requests.get(url = 'http://localhost:' + portList[i] + '/api/v1/_health')
            if res.status_code == 500:
                # stop container 
                # remove container
                # start container
        sleep(1)