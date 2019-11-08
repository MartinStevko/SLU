# SLU
SLU enrollment and other organization stuffs.

## Requirements installation

 - virtual enviroment
 - Python (3 or later, version 3.7 recommended)
 - requirements.txt

### Windows machine
Install Python from https://www.python.org/downloads/ and then in CMD type:

```cmd
py -m pip install virtualenv
```
### Linux machine
In Bash type:

```bash
sudo apt install pip
```
```bash
python3 -m pip install virtualenv
```

## Server setup for local network

You have to get through local setup only once (per a project).

First, create `app/local_settings.py` file from template in the same directory.

### Windows machine

Then, in CMD:

Create virtual enviroment
```cmd
py -m venv ENV_NAME
```
activate it
```cmd
ENV_NAME\Scripts\activate
```
and install all requirements by typing
```cmd
py -m pip install -r requirements.txt
```
to your administrator command line inside `SLU` directory.

Perhaps, you will need to allow remote access in your firewall.

### Linux machine

Then, in Terminal:

Create virtual enviroment
```bash
virtualenv ENV_NAME
```
activate it
```bash
source ENV_NAME/bin/activate
```
and install all requirements by typing
```bash
sudo pip install -r requirements.txt
```
inside `SLU` directory and allow remote access for desired port:
```bash
iptables -I INPUT -p tcp -m tcp --dport PORT_NUMBER -j ACCEPT
```

## Base database creation

Apply all migrations. You can do it by typing:

```cmd
py manage.py migrate
```

to your CMD or 

```bash
python3 manage.py migrate
```

to your Terminal into `SLU` directory.


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
py manage.py runserver 0.0.0.0:PORT_NUMBER
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

After all that you can access to admin site by typing `localhost:PORT_NUMBER/admin` and to app by typing `localhost:PORT_NUMBER` (`localhost` can be substituted by an IP address of server e.g. `192.168.1.47`).
