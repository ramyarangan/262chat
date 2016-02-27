'''
Handlers for requests from web browsers or other clients. 
'''

from flask import render_template, request, Response, jsonify
from app import app
import json

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

@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

def response_ok():
	resp = jsonify({})
	resp.status_code = 200
	return resp

## ACCOUNTS 

@app.route('/accounts/create', methods=['GET', 'POST'])
def create_account():
	# XXX TODO CREATE FOR REAL
	user = request.data.username
	return response_ok()

@app.route('/accounts/delete', methods=['GET', 'POST'])
def delete_account():
	# XXX TODO CREATE FOR REAL
	user = request.data.username
	return response_ok()

@app.route('/accounts/login', methods=['GET', 'POST'])
def login():
	# if username failed then..
	# return not_found()
	# else, log in and response_ok
	# XXX TODO LOGIN FOR REAL
    return response_ok() 

@app.route('/accounts/logout', methods=['GET', 'POST'])
def logout():
	# XXX TODO LOGOUT FOR REAL; is this just a no-op?
    return response_ok()

@app.route('/accounts/search/<query>', methods=['GET', 'POST'])
def search_accounts(query):
	account_list = ["1", "2"]
	data = {
		"accounts": account_list
	}
	js = json.dumps(data)

	resp = jsonify(data)
	resp.status_code = 200
	return resp

## GROUPS

@app.route('/groups/create', methods=['GET', 'POST'])
def create_group():
	# XXX TODO CREATE FOR REAL
	creator = request.data.creator
	return response_ok()

@app.route('/groups/search/<query>', methods=['GET', 'POST'])
def search_groups(query):
	return response_ok()

## MESSAGES 

@app.route('/messages/fetch', methods=['GET', 'POST'])
def fetch_messages():
	user = request.data.username
	return response_ok()

@app.route('/messages/fetch-undelivered', methods=['GET', 'POST'])
def fetch_undelivered_messages():
	user = request.data.username
	return response_ok()

@app.route('/messages/send', methods=['POST'])
def send_message():
	sender = request.data.sender
	to = request.data.to
	return response_ok()

@app.route('/messages/ack', methods=['GET', 'POST'])
def ack_message():
	user = request.data.username
	messages = request.data.messages
	return response_ok()