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
