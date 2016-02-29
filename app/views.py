'''
Handlers for requests from web browsers or other clients. 
'''

from flask import render_template, request, Response, jsonify
from sqlalchemy import exc
from app import app, db, models
import json

DEBUG = 1

@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

def response_ok(data={}):
	resp = jsonify(data)
	resp.status_code = 200
	return resp

## ACCOUNTS 

@app.route('/accounts/create', methods=['POST'])
def create_account():
	# XXX TODO CREATE FOR REAL
	parsed_json = json.loads(request.data)
	username = parsed_json["username"]

	user = models.User(username=username)
	try:
		db.session.add(user)
		db.session.commit()
		return response_ok()
	except exc.IntegrityError:
		print("Duplicate username")
        db.session.rollback()
        return not_found() # TODO XXX
    
def get_user_by_username(username):
	return models.User.query.filter_by(username=username).first()

@app.route('/accounts/delete', methods=['GET', 'POST'])
def delete_account():
	# XXX TODO CREATE FOR REAL
	parsed_json = json.loads(request.data)
	username = parsed_json["username"]

	user = get_user_by_username(username)
	if user:
		db.session.delete(user)
		try:
  			db.session.commit()
  			return response_ok()
		except exc.SQLAlchemyError:
			#TODO
  			pass
	else:
		## TODO user not found error
		pass 

@app.route('/accounts/login', methods=['POST'])
def login():
	parsed_json = json.loads(request.data)
	username = parsed_json["username"]

	user = get_user_by_username(username)
	if user:
		# TODO validate password
		return response_ok()
	else:
		return not_found() ## TODO FIX

#@app.route('/accounts/logout', methods=['GET', 'POST'])
#def logout():
	# XXX MAYBE WE SHOULD DELETE THIS FUNCTION
#    return response_ok()

@app.route('/accounts/search', methods=['POST'])
def search_users():
	parsed_json = json.loads(request.data)
	query = parsed_json['query']

	# match SQLalchemy search syntax
	query = query.replace('*', '%')

	# query the database for matching usernames
	matches = models.User.query.filter(models.User.username.like(query)).all()
	match_names = [match.username for match in matches]

	data = {
		"accounts": match_names
	}
	return response_ok(data)


## GROUPS

@app.route('/groups/create', methods=['GET', 'POST'])
def create_group():
	parsed_json = json.loads(request.data)
	creator = parsed_json["creator"]
	users = parsed_json["users"]
	groupname = parsed_json["groupname"]
	return response_ok()

	user = models.User(username=username)
	try:
		db.session.add(user)
		db.session.commit()
		return response_ok()
	except exc.IntegrityError:
		print("Duplicate username")
        db.session.rollback()
        return not_found() # TODO XXX
    


def search_by_groupname(fmt_query):
	# query the database for matching groupnames
	matches = models.Group.query.filter(models.Group.groupname.like(fmt_query)).all()
	
	return set(matches)

def search_by_username(fmt_query):
	# query database for matching usernames
	group_set = set()
	matches = models.User.query.filter(models.User.username.like(fmt_query)).all()
	for user in matches:
		group_set |= set(user.groups)

	return group_set

# TODO: Need to handle responses if we have non-unique groupnames
@app.route('/groups/search', methods=['GET', 'POST'])
def search_groups():
	parsed_json = json.loads(request.data)
	query = parsed_json['query']

	# match SQLalchemy search syntax
	fmt_query = query.replace('*', '%')

	groupname_search_set = search_by_groupname(fmt_query)
	username_search_set = search_by_username(fmt_query) - groupname_set

	data = {
		"groups_by_groupname": [group.groupname for group in groupname_search_set],
		"groups_by_username": [group.groupname for group in groupname_search_set],
	}

	return response_ok(data)


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