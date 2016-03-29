# 262chat


## Setup

1. Clone the [Github repo] (https://github.com/ramyarangan/262chat.git). 
   All paths are now relative to the top-level directory.

2. Follow the instructions [here](http://flask.pocoo.org/docs/0.10/installation/)
   to set up Flask.

3. Activate the virtual environment with `. /venv/bin/activate`.

4. Enter `pip install -r requirements.txt` to install necessary dependencies. 

5. Run `./db_create` to initialize the database.


## Running

### Server
`./run.py` launches the server at <http://localhost:5000>.

### Client
Configure the client to point to the public IP/port of the machine on which 
the server is running by modifying “SERVER_IP” and "SERVER_PORT" in 
`client/client.py`. To run, use `python client/client.py`. 