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

	data = {
		"messages": [message.body for message in message_list],
		"ids": [message.id for message in message_list],
		"authors": [message.sender_username for message in message_list],
		"group": [message.to_group for message in message_list]
	} 
	resp = jsonify(data)
	resp.status_code = 200
	return resp

@app.route('/messages/fetch-undelivered', methods=['POST'])
def fetch_undelivered_messages():
	parsed_json = json.loads(request.data)
	user = parsed_json["to"]
	from_user = parsed_json["from"]

	# get only the unseen messages from "from_user"
	seen_msg = models.Seen.query.filter( \
		(models.Seen.viewer == user) & \
		(models.Seen.room_user == from_user)).first()
	msgs = []
	last_id = None
	if (seen_msg != None):
		last_id = seen_msg.last_seen_id
		msgs = models.Message.query.filter( \
			(models.Message.to_username == user) & \
			(models.Message.sender_username == from_user) & \
			(models.Message.id > last_id)). \
			order_by(models.Message.id).all()

	data = {
		"messages": [msg.body for msg in msgs],
		"ids": [msg.id for msg in msgs],
		"last_id": last_id
	}
	resp = jsonify(data)
	resp.status_code = 200
	return resp

@app.route('/messages/fetch-undelivered-group', methods=['POST'])
def fetch_undelivered_messages_group():
	parsed_json = json.loads(request.data)
	to_user = parsed_json["to"]
	from_group = parsed_json["from"]

	# Get these messages from everyone in the specified group
	users = get_users_by_groupname(from_group)
	usernames = [user.username for user in users]
	usernames = [user for user in usernames if (user != to_user)]

	seen_msg = models.Seen.query.filter( \
		(models.Seen.viewer == to_user) & \
		(models.Seen.room_group == from_group)).first()
	msgs = []
	last_id = None
	if (seen_msg != None):
		last_id = seen_msg.last_seen_id
		if (last_id == 0):
			last_id = last_id - 1
		msgs = models.Message.query.filter( \
			(models.Message.to_groupname == from_group) & \
			(models.Message.sender_username.in_(usernames)) & \
			(models.Message.id > last_id)). \
			order_by(models.Message.id).all()

	data = {
		"messages": [msg.body for msg in msgs],
		"authors": [msg.sender_username for msg in msgs],
		"ids": [msg.id for msg in msgs],
		"last_id": last_id
	}
	resp = jsonify(data)
	resp.status_code = 200
	return resp

# here also add to last seen table
@app.route('/messages/send', methods=['POST'])
def send_message():
	parsed_json = json.loads(request.data)
	sender = parsed_json["sender"]
	to = parsed_json["to"]
	message = parsed_json["message"]

	m = models.Message(body=message, timestamp=datetime.now(),\
		sender_username=sender, to_groupname = None, to_username=to)
	db.session.add(m)

	s = models.Seen(viewer=to, room_user=sender, room_group=None)
	db.session.add(s)

	try:
		db.session.commit()
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

	m = models.Message(body=message, timestamp=datetime.now(),\
	sender_username=sender, to_groupname=to_group, to_username=None)
	db.session.add(m)
	try:
		db.session.commit()
	except exc.SQLAlchemyError:
		#TODO
		pass

	for to in to_group_users:
		in_db = models.Seen.query.filter( \
			(models.Seen.viewer == to) & \
			(models.Seen.room_user == None) & \
			(models.Seen.room_group == to_group)).all()
		if (len(in_db) == 0):
			s = models.Seen(viewer=to, room_user=None, room_group=to_group)
			db.session.add(s)
			try:
				db.session.commit()
			except exc.SQLAlchemyError:
				#TODO
				pass

	return response_ok()

@app.route('/messages/ack', methods=['GET', 'POST'])
def ack_last_message():
	parsed_json = json.loads(request.data)
	viewer = parsed_json["viewer"]
	room_user = parsed_json.get("room_user")
	room_group = parsed_json.get("room_group")
	last_seen_id = parsed_json["last_seen_id"]

	if not (room_user or room_group):
		print "Invalid parameters"
		#TODO
		return not_found()

	msgs = models.Seen.query.filter_by(viewer=viewer)
	msg = msgs.first() 
	if (room_group != None):
		msg = msgs.filter_by(room_group=room_group).first()
	if (room_user != None):
		msg = msgs.filter_by(room_user=room_user).first()
	
	if not msg:
		print "Could not find chatroom in database"
		#TODO
		return not_found()

	msg.last_seen_id = max(last_seen_id, msg.last_seen_id)
	try:
		db.session.commit()
		return response_ok()
	except exc.SQLAlchemyError:
		#TODO
		db.session.rollback()
		pass
