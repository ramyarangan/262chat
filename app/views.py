'''
Handlers for requests from web browsers or other clients. 
'''

from flask import render_template, request, Response, jsonify
from sqlalchemy import exc
from app import app, db, models
import json
from datetime import datetime

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

def get_users_by_groupname(groupname):
	group = models.Group.query.filter_by(groupname=groupname).first()
	return group.users

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
	usernames = parsed_json["usernames"]
	groupname = parsed_json["groupname"]
	
	print creator
	print usernames
	print groupname

	# Validate and retrieve users
	if creator not in usernames:
		print "Error: creator not included in user list"
		# Should never happen with our client, but enforce that creator is included in group 
		return not_found() # TODO XXX
	users = []
	for username in usernames:
		user = get_user_by_username(username)
		if not user:
			# User does not exist D:
			print "Error: user %s does not exist" % username
			return not_found() # TODO XXX
		users.append(user)

	# Create the group
	group = models.Group(groupname=groupname)	
	try:
		db.session.add(group)

	    # Add users to the group
		for user in users:
			group.users.append(user)

	    # Woohoo!
		db.session.commit()
		return response_ok()
	except exc.IntegrityError:
		print "Error: Duplicate groupname"
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
	username_search_set = search_by_username(fmt_query) - groupname_search_set
	print username_search_set

	data = {
		"groups_by_groupname": [group.groupname for group in groupname_search_set],
		"groups_by_username": [group.groupname for group in username_search_set],
	}

	return response_ok(data)

## MESSAGES 
# TODO: Check that messages are sent to people in the database, and so on
# Basically all error checking.
@app.route('/messages/fetch', methods=['GET', 'POST'])
def fetch_messages():
	parsed_json = json.loads(request.data)
	user = parsed_json["username"]

	message_list = models.Message.query.filter_by(to_username=user).all()
	for message in message_list:
		message.received = models.Message.STATUS_PENDING
	try:
		db.session.commit()
		return response_ok()
	except exc.SQLAlchemyError:
		#TODO
		pass

	data = {
		"messages": [message.body for message in message_list],
		"ids": [message.id for message in message_list]
	}
	resp = jsonify(data)
	resp.status_code = 200
	return resp

def query_messages_to_send(user, from_user):
	message_list = models.Message.query.filter_by(to_username=user)
	message_list = message_list.filter_by(sender_username=from_user)
	message_list = message_list.filter_by(received=models.Message.STATUS_NEW)
	message_list = message_list.all()
	for message in message_list:
		message.received = models.Message.STATUS_PENDING
	try:
		db.session.commit()
		return response_ok()
	except exc.SQLAlchemyError:
		#TODO
		pass

	message_texts = [message.body for message in message_list]
	message_times = [message.timestamp for message in message_list]
	message_ids = [message.id for message in message_list]
	#return zip(message_texts, message_times, message_ids)
	return [(1,2,3),(1,2,3),(1,2,3)]

@app.route('/messages/fetch-undelivered', methods=['POST'])
def fetch_undelivered_messages():
	parsed_json = json.loads(request.data)
	user = parsed_json["to_user"]
	from_user = parsed_json["from_name"]
	# get only the messages from "from_user"
	text_times = query_messages_to_send(user, from_user)

	messages_sorted = sorted(text_times, key=lambda message : message[1])
	messages = [message[0] for message in messages_sorted]
	ids = [message[2] for message in messages_sorted]
	data = {
		"messages": messages,
		"ids": ids
	}
	resp = jsonify(data)
	resp.status_code = 200
	return resp

@app.route('/messages/fetch-undelivered-group', methods=['POST'])
def fetch_undelivered_messages_group():
	parsed_json = json.loads(request.data)
	to_user = parsed_json["to_user"]
	from_group = parsed_json["from_name"]
	# Get these messages from everyone in the specified group
	users = get_users_by_groupname(from_group)
	usernames = [user.username for user in users]
	messages = []
	for from_user in usernames:
		text_times = query_messages_to_send(to_user, from_user)
		text_time_users = [(text_time[0], text_time[1], text_time[2], from_user) \
										for text_time in text_times]
		messages = messages + text_time_users

	messages_sorted = sorted(messages, key = lambda message: message[1])
	data = {
		"messages": [message[0] for message in messages_sorted],
		"authors": [message[3] for message in messages_sorted],
		"ids": [message[2] for message in messages_sorted]
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

	m = models.Message(body=message, timestamp=datetime.now(),\
		received=models.Message.STATUS_NEW, sender_username=sender,\
		to_username=to)
	db.session.add(m)
	try:
		db.session.commit()
		return response_ok()
	except exc.SQLAlchemyError:
		#TODO
		pass

	return response_ok()

@app.route('/messages/send-group', methods=['POST'])
def send_message_group():
	parsed_json = json.loads(request.data)
	sender = parsed_json["sender"]
	to_group = parsed_json["to"] # Now this is a group name.. send to everyone in group
	message = parsed_json["message"]

	users = get_users_by_groupname(to_group)
	to_group_users = [user.username for user in users]

	for to in to_group_users:
		m = models.Message(body=message, timestamp=datetime.now(),\
		received=models.Message.STATUS_NEW, sender_username=sender,\
		to_username=to)
		db.session.add(m)
		try:
			db.session.commit()
			return response_ok()
		except exc.SQLAlchemyError:
			#TODO
			pass

	return response_ok()

@app.route('/messages/ack', methods=['GET', 'POST'])
def ack_message():
	user = request.data.username
	messages = request.data.messages
	return response_ok()