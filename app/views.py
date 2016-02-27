'''
Handlers for requests from web browsers or other clients. 
'''

from flask import render_template, request, Response, jsonify
from app import app, models
import json


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

@app.route('/accounts/create', methods=['POST'])
def create_account():
	# XXX TODO CREATE FOR REAL
	parsed_json = json.loads(request.data)
	user = parsed_json["username"]
	return response_ok()

@app.route('/accounts/delete', methods=['GET', 'POST'])
def delete_account():
	# XXX TODO CREATE FOR REAL
	parsed_json = json.loads(request.data)
	user = parsed_json["username"]
	return response_ok()

@app.route('/accounts/login', methods=['POST'])
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

@app.route('/accounts/search/', methods=['POST'])
def search_accounts():
	parsed_json = json.loads(request.data)
	query = parsed_json["query"]
	account_list = ["user1", "user2"]
	data = {
		"accounts": account_list
	}
	resp = jsonify(data)
	resp.status_code = 200
	return resp

## GROUPS

@app.route('/groups/create', methods=['GET', 'POST'])
def create_group():
	parsed_json = json.loads(request.data)
	creator = parsed_json["username"]
	users = parsed_json["user_list"]
	group_name = parsed_json["group_name"]
	return response_ok()

@app.route('/groups/search/<query>', methods=['GET', 'POST'])
def search_groups(query):
	parsed_json = json.loads(request.data)
	query = parsed_json["query"]
	group_list = ["group1", "group2"]
	data = {
		"groups": group_list
	}
	resp = jsonify(data)
	resp.status_code = 200
	return resp

## MESSAGES 

@app.route('/messages/fetch', methods=['GET', 'POST'])
def fetch_messages():
	parsed_json = json.loads(request.data)
	user = parsed_json["username"]

	messages = ["blah", "you suck", "these are great messages"]
	data = {
		"messages": messages
	}
	resp = jsonify(data)
	resp.status_code = 200
	return resp

@app.route('/messages/fetch-undelivered', methods=['POST'])
def fetch_undelivered_messages():
	parsed_json = json.loads(request.data)
	user = parsed_json["to_user"]
	from_user = parsed_json["from_name"]
	# get only the messages from "from_user"
	messages = ["blah", "you suck", "these are great messages"]
	data = {
		"messages": messages
	}
	resp = jsonify(data)
	resp.status_code = 200
	return resp

@app.route('/messages/fetch-undelivered-group', methods=['POST'])
def fetch_undelivered_messages_group():
	parsed_json = json.loads(request.data)
	user = parsed_json["to_user"]
	from_user = parsed_json["from_name"]
	# Get these messages from everyone in the specified group
	messages = ["blah", "you suck", "these are great messages"]
	data = {
		"messages": messages
	}
	resp = jsonify(data)
	resp.status_code = 200
	return resp

@app.route('/messages/send', methods=['POST'])
def send_message():
	parsed_json = json.loads(request.data)
	sender = parsed_json["sender"]
	to = parsed_json["to"]
	message = parsed_json["message"]
	return response_ok()

@app.route('/messages/send-group', methods=['POST'])
def send_message_group():
	parsed_json = json.loads(request.data)
	sender = parsed_json["sender"]
	to = parsed_json["to"] # Now this is a group name.. send to everyone in group
	message = parsed_json["message"]
	return response_ok()

@app.route('/messages/ack', methods=['GET', 'POST'])
def ack_message():
	user = request.data.username
	messages = request.data.messages
	return response_ok()