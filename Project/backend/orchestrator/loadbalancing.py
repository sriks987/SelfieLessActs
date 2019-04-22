import os
import requests
import logging
from time import sleep
from flask import Flask, request, Response, abort, render_template
#import docker

#client = docker.from_env()

#client.containers.run("acts", detach=True)

#list_containers = client.containers.list()

#os.system("docker rm $(docker container ps -a --last 2 -q)")

app = Flask(__name__)
portLists = [8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8010]
containerIDs = []
index = 0

@app.route("/api/v1/<path:remaining>", methods=["GET", "POST", "PUT", "DELETE"])
def function(remaining):
        global index
        app.logger.warning(remaining)
        var = str(requests.get(url = 'http://127.0.0.1:' + str(portLists[index]) + '/api/v1/' + remaining).json())
        app.logger.warning(portLists[index])
        index = (index + 1)%(len(portLists))
        return var


if __name__ == '__main__':
        app.logger.warning("hello")

        app.run(host='0.0.0.0', port=80)
