'''
Handlers for requests from web browsers or other clients. 
'''

from flask import render_template, request
from app import app, models

RESPONSE_OK = 'Success\n'

@app.route('/')
@app.route('/index')
def index():
    messages = [  # fake array of posts
        { 
            'from': 'Ramya', 
            'body': 'I\'m on the shuttle!' 
        },
        { 
            'from': 'everyone', 
            'body': 'LOL' 
        }
    ]
    return render_template("messages.txt",
                           messages=messages)


## ACCOUNTS 

@app.route('/accounts/create', methods=['GET', 'POST'])
def create_account():
	user = models.User(request.data)
	db.session.add(user)
	db.session.commit()

	return RESPONSE_OK

@app.route('/accounts/delete', methods=['GET', 'POST'])
def delete_account():
	# XXX TODO CREATE FOR REAL
	user = request.data.username
	return RESPONSE_OK

@app.route('/accounts/login', methods=['GET', 'POST'])
def login():
	# XXX TODO LOGIN FOR REAL
    return RESPONSE_OK 

@app.route('/accounts/logout', methods=['GET', 'POST'])
def logout():
	# XXX TODO LOGOUT FOR REAL; is this just a no-op?
    return RESPONSE_OK

@app.route('/accounts/search/<query>', methods=['GET', 'POST'])
def search_accounts(query):
	return RESPONSE_OK


## GROUPS

@app.route('/groups/create', methods=['GET', 'POST'])
def create_group():
	# XXX TODO CREATE FOR REAL
	creator = request.data.creator
	return RESPONSE_OK

@app.route('/groups/search/<query>', methods=['GET', 'POST'])
def search_groups(query):
	return RESPONSE_OK


## MESSAGES 

@app.route('/messages/fetch', methods=['GET', 'POST'])
def fetch_messages():
	user = request.data.username
	return RESPONSE_OK

@app.route('/messages/fetch-undelivered', methods=['GET', 'POST'])
def fetch_undelivered_messages():
	user = request.data.username
	return RESPONSE_OK

@app.route('/messages/send', methods=['POST'])
def send_message():
	sender = request.data.sender
	to = request.data.to
	return RESPONSE_OK

@app.route('/messages/ack', methods=['GET', 'POST'])
def ack_message():
	user = request.data.username
	messages = request.data.messages
	return RESPONSE_OK


