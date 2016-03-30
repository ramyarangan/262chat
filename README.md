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

TODO

MVC architecture, blah blah blah

The server is built on the Python web microframework [Flask](http://flask.pocoo.org/). It persists data in an [SQLAlchemy](http://www.sqlalchemy.org/) database, integrated using the [Flask-SQLAlchemy extension](http://flask-sqlalchemy.pocoo.org/2.1/). To manage database creation and updates, we use the [SQLAlchemy-Migrate extension](https://sqlalchemy-migrate.readthedocs.org/). 

## Files

### General setup
* `config.py`
* `requirements.txt`

### Database setup
* `db_create.py`
* `db_downgrade.py`
* `db_migrate.py`
* `db_upgrate.py`

### Server
* `run.py`
* `app/`
	* `__init__.py`
	* `models.py`
	* `views.py`
* `client/`
	* `client.py`
