# 262chat

This is a chat application that supports private and group chats. 

## Installation

1. Clone the [Github repo](https://github.com/ramyarangan/262chat.git). 
   All paths are now relative to the top-level directory.
   ``` 
   git clone https://github.com/ramyarangan/262chat.git 
   ```

2. Install Python dependencies. We suggest using a virtual environment to manage them, as follows:

	* Install [virtualenv](http://flask.pocoo.org/docs/0.10/installation/) if you don't have it already.

	``` 
	sudo pip install virtualenv
	```

	* Initialize the virtual environment.
	```
	virtualenv venv
	```

	* Activate the environment.
	```
	. venv/bin/activate
	```
	
	* Install all necessary dependencies (into the venv).
	```
	pip install -r requirements.txt
	```

3. Initialize the database. This will create a folder `db_repository` in the project root, where the server will store the database data as well as metadata for migrations.
``` 
./db_create 
```


## Running

### Server
`./run.py` launches the server at <http://localhost:5000>.

### Client
Configure the client to point to the public IP/port of the machine on which 
the server is running by modifying `SERVER_IP` and `SERVER_PORT` in 
`client/client.py`. To run, use `python client/client.py`. 


## Architecture

This is a chat application using the REST protocol to communicate between clients and the server. 

Our server was built using Flask, a lightweight web framework built on Python. Using Flask allowed us to easily create relevant databases and provided a convenient wrapper around REST requests. We use the MVC framework for this purpose, specifying the database in models.py (Model), and the server API in views.py (Controller).

The server can accept requests from clients on other devices which hit the server machine’s public IP address. 

The server provides an API for clients to carry out basic operations to manipulate the chat system, with REST endpoints for instance hitting functions like fetch_unread_messages, or create_new_user. These REST endpoints communicate data via JSON strings, representing data structures transferred through POST requests. Internally, to carry out these operations, these server functions manipulate and/or read from the appropriate server-side SQL tables storing information about users, groups, messages, and message read history. 

Our client is a terminal chat application, which hits the server's API endpoints to allow individuals to manage users and groups, enter chatrooms, and chat with others in these rooms. While our client is currently a simple Python application, the REST-based Flask server poses few limitations on the client’s structure -- any language or framework can work. 

We chose to require that the client handle login and logout functionality - when logging in, the user’s username information is stored on the client, and the client ensures that functions requiring authentication cannot carry out without the user’s login. This choice allows the server to save less state, for instance removing the need for storing current user ids in a server-side session. We require that users only be logged into the chat application from one device at a time, simplifying the logic of retrieving unread messages.

We handle errors by sending appropriate REST status codes in responses from the server to the client. For instance, when an invalid username is used for login, the server’s response to the client contains the status code 401 and a helpful message signaling unauthorized use. We are particularly careful when sending recent messages stored in the server’s databases to the client. Indeed, according to the specifications, upon sending new messages, the server must mark the messages as read in the database such that they will not be sent to the client again on future requests for messages. Thus, it is especially essential to ensure that the messages that are sent only once to the client are truly received over the network, to prevent the client from irrevocably missing messages. To ensure this, the client sends the server an ack message with message id’s it has seen; only upon receiving this ack message does the server mark these messages as read. For more details, 
refer to comments on class Seen, at models.py:22.


## Imports

### Included in requirements.txt 
* The server is built on the Python web microframework [Flask](http://flask.pocoo.org/). 
* It persists data in an [SQLAlchemy](http://www.sqlalchemy.org/) database, integrated using the [Flask-SQLAlchemy extension](http://flask-sqlalchemy.pocoo.org/2.1/). 
* To manage database creation and updates, we use the [SQLAlchemy-Migrate extension](https://sqlalchemy-migrate.readthedocs.org/). 
* To communicate between the server and client via REST, we use the [requests](http://docs.python-requests.org/en/master/) Python module. 

## Files

### General setup
* `config.py` - required for Flask setup
* `requirements.txt` - imports

### Database setup
* `db_create.py`
* `db_downgrade.py`
* `db_migrate.py`
* `db_upgrate.py`

### Chat Application Server
* `run.py` - launches server
* `app/`
	* `__init__.py`
	* `models.py` - database with tables for messages, message seen history, users, and groups
	* `views.py` - API calls provided by the chat application server

### Chat Application Client
* `client/`
	* `client.py` - creates terminal chat application, which interacts with chat server
