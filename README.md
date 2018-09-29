# SLU
SLU enrollment and other organization stuffs.

## Requirements installation

 - Python (3 or later, version 3.7.0 recommended)
 - Django (version 2.1)
 - virtual enviroment

### Windows machine
Install Python from https://www.python.org/downloads/ and then in CMD type:

```cmd
py -m pip install Django==2.0
```
```cmd
py -m pip install virtualenv
```
### Linux machine
In Bash type:

```bash
sudo apt install pip
```
```bash
python3 -m pip install Django==2.1
```
```bash
python3 -m pip install virtualenv
```

## Server setup for local network

You have to get through local setup only once (per a project).

### Windows machine

In CMD:

Create virtual enviroment
```cmd
py -m venv ENV_NAME
```
Perhaps, you will need to allow remote access in your firewall.

### Linux machine

In Terminal:

Create virtual enviroment
```cmd
virtualenv ENV_NAME
```
and allow remote access for desired port:
```bash
iptables -I INPUT -p tcp -m tcp --dport PORT_NUMBER -j ACCEPT
```

## Base database creation

Make and then apply migrations. You can do it by typing:

```
py manage.py makemigrations organization
```
```
py manage.py migrate
```

to your CMD or 

```
python3 manage.py makemigrations organization
```
```
python3 manage.py migrate
```

to your Bash into `SLU` directory.


## Run server

### Windows machine

In CMD:

1. Go to `SLU` directory
2. Activate your virtual environment:
```cmd
ENV_NAME\Scripts\activate
```
3. Run server on your desired port:
```cmd
python manage.py runserver 0.0.0.0:PORT_NUMBER
```

### Linux machine

1. Login as root user

In Terminal:

2. Go to `SLU` directory
3. Activate your virtual environment:
```bash
source ENV_NAME/bin/activate
```
4. Run server on your desired port:
```bash
python manage.py runserver 0.0.0.0:PORT_NUMBER
```

## Application access

After all that you can access to admin site by typing `localhost:PORT_NUMBER/admin` and to app by typing `localhost:PORT_NUMBER/index` (`localhost` can be substituted by an IP address of server e.g. `192.168.1.47`).
