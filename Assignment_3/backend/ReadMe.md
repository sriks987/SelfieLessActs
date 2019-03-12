# Helper Guide to Assignment 3

## Instance

- Go to your amazon console and create an EC2 Instance with the following specifications - 
    * Ubuntu 16.04
    * Security Groups - 
        - Custom TCP Rule - 8000 (For Acts API)
        - Custom TCP Rule - 8080 (For Users API)
        - SSH
        - HTTP


## Dockers 

- Switch to root - sudo su
- Install Docker using the following commands - 
```console
    apt-get update
```
```console
    apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common
```
```console
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```
```console
    sudo apt-key fingerprint 0EBFCD88
```
```console
    sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
```
```console
    apt-get update
```
```console
    apt-get install docker-ce docker-ce-cli containerd.io
```

- Verify the installation by running - 
```console
    docker run hello-world
```

- Docker Commands - 
    * Run to destroy all docker images. However, containers that were running in "detached" mode aren't removed.
    ```console
        docker system prune -a
    ```
    * To list all docker images - 
    ```console
        docker image ls
    ```
    * To list all docker containers - 
    ```console 
        docker container ls
    ```
    * To stop docker container - 
    ```console 
        docker container stop <containerID>
    ```
    * To remove docker container - 
    ```console
        docker container rm <containerID>
    ```

## Docker Hub

- Go to hub.docker.com and create an account
- Keep your credentials safe as you will need it later.

## Assignment in itself

- Create a folder called "users" in /home/ubuntu
```console
   mkdir users
```
- Enter the directory - 
```console
   cd users
```
- In this directory, download the Dockerfile and app.py file for *users*. On ls, you must be able to see two files - Dockerfile & app.py

- Create a folder called "acts" in /home/ubuntu
```console
   mkdir acts
```

- Enter the directory -
```console
   cd acts
```

- In this directory, download the Dockerfile and app.py file for *acts*. On ls, you must be able to see two files - Dockerfile & app.py

- MongoDB - 
   * Pull the MongoDB alpine image using - 
   ```console
      docker pull mvertes/alpine-mongo
   ```
   * Run the image you have just pulled - 
   ```console
      docker run -d --name mongo -p 27017:27017 mvertes/alpine-mongo
   ```
   * To connect to MongoDB container, you need to know the IP of the container. Get the IP using - 
   ```console
      docker network inspect bridge
   ```
   * Use the IPv4 address (without subnet) and substitute that in your app.py code - 
   ```code
      client = MongoClient("IPv4", 27017)
   ```
- Build the Image for users - 
```console
   docker build --tag=users .
```
- Run the image - 
```console 
   docker run -d --name users -p 8080:8080 users
```

- Build the Image for acts - 
```console
   docker build --tag=acts .
```
- Run the image - 
```console
   docker run -p 8000:8000 acts
```

## Postman

- For users - IP:8080/apicalls
- For acts - IP:8000/apicalls
   
## Communication between User and Act Containers 

- All containers are present within the same network.
- It is easy to communicate if IPs of the containers are known.
- The following command helps to get to know the IPs of the containers.
```console
   docker network inspect bridge
```
- This can be used in acts/app.py to communicate with users container
```code
   newIP = "http://IP:port"
```
