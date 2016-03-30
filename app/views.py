'''
This file is the 'View' part of the chat application's MVC architecture.
It contains handlers for requests from clients. 

Each handler catches requests sent to the server at the route specified
in its arguments. At the time of execution, the object `request` represents 
the current request being handled.
'''

#==================================
# IMPORTS

# Flask microframework utilities: 
#   `request` is an object that represents the current request being handled
#   `jsonify` is a utility function Creates a flask.Response (HTTP response) object 
#        with the JSON representation of given arguments with an application/json mimetype.
from flask import request, jsonify

# Database exception handlers: `exc` is SQLAlchemy's exception suite
from sqlalchemy import exc

# Flask framework components:
#   `app` is an instance of class `Flask` and represents the
#        application itself
#   `db` represents the (SQLAlchemy-powered) database
#   `models` are our data models, as defined in models.py
from app import app, db, models

# Package of JSON utilities, used to parse messages between client
import json

# Used to record time of message receipt by the server
from datetime import datetime


#==================================
# ERROR HANDLERS

@app.errorhandler(404)
def not_found(message = ""):
    """
    Send an HTTP response signaling that the request was intended for
    an unhandled route, along with an optional error message.

    Args:
        message: Error message intended for the client.
            type: string

    Returns: 
        HTTP response object with status set to 404 (Not found), mimetype
        as application/json, and passed-in `message` encoded in JSON with key 'message'.
            type: flask.Response
    """

    message = 'Not Found: ' + request.url
    print message
    data = {
        'message': message,
    }
    resp = jsonify(data)
    resp.status_code = 404

    return resp

@app.errorhandler(400)
def error_invalid_params(message = ""):
    """
    Send an HTTP response signaling that the request has invalid 
    or malformed parameters along with an optional error message.

    Args:
        message: Error message intended for the client.
            type: string

    Returns: 
        HTTP response object with status set to 400 (Bad request), mimetype
        as application/json, and passed-in `message` encoded in JSON with key 'message'.
            type: flask.Response
    """

    print message
    data = {
        'message': message,
    }
    resp = jsonify(data)
    resp.status_code = 400
    return resp

@app.errorhandler(401)
def error_unauthorized(message = ""):
    """
    Send an HTTP response signaling unauthorized access (status code 401), 
    along with an optional error message.

    Args:
        message: Error message intended for the client.
            type: string

    Returns: 
        HTTP response object with status set to 401 (Unauthorized), mimetype
        as application/json, and passed-in `message` encoded in JSON with key 'message'.
            type: flask.Response
    """

    print message
    data = {
        'message': message,
    }
    resp = jsonify(data)
    resp.status_code = 401
    return resp

@app.errorhandler(403)
def error_forbidden(message = ""):
    """
    Send an HTTP response signaling forbidden access (status code 403), 
    along with an optional error message.

    Args:
        message: Error message intended for the client.
            type: string

    Returns: 
        HTTP response object with status set to 403 (Forbidden), mimetype
        as application/json, and passed-in `message` encoded in JSON with key 'message'.
            type: flask.Response
    """

    print message
    data = {
        'message': message,
    }
    resp = jsonify(data)
    resp.status_code = 403
    return resp

@app.errorhandler(500)
def error_internal_server(message = ""):
    """
    Send an HTTP response signaling an internal server error, 
    along with an optional error message.

    Args:
        message: Error message intended for the client.
            type: string

    Returns: 
        HTTP response object with status set to 500 (Internal server error), mimetype
        as application/json, and passed-in `message` encoded in JSON with key 'message'.
            type: flask.Response
    """

    print message
    data = {
        'message': message,
    }
    resp = jsonify(data)
    resp.status_code = 500
    return resp

def response_ok(data={}):
    """
    Send an HTTP response signaling success, along with any data 
    the client might be interested in.

    Args:
        data: Any data that the server wishes to pass to the client
            type: dict

    Returns: 
        HTTP response object with status set to 200 (OK), mimetype
        as application/json, and `data` encoded in JSON format.
            type: flask.Response
    """

    resp = jsonify(data)
    resp.status_code = 200
    return resp


#==================================
# ACCOUNTS 

def get_user_by_username(username):
    """
    Fetch data corresponding to the user with the specified username 
    from the database.

    Args:
        username: the username of interest
            type: string

    Returns: 
        Object representing data corresponding to the user of interest,
        or None if no matching user was found
            type: models.User
    """
    return models.User.query.filter_by(username=username).first()

@app.route('/accounts/create', methods=['POST'])
def create_account():
    """
    Creates a new account in the database. Fails if the account already exists.

    HTTP request arguments:
        `username`: the username of the desired new account

    Returns: 
        HTTP response object for the client, indicating whether / how the 
        creation attempt succeeded or failed.
            type: flask.Response
    """
    parsed_json = json.loads(request.data)
    username = parsed_json["username"]

    user = models.User(username=username)
    try:
        db.session.add(user)
        db.session.commit()
        return response_ok()
    except exc.IntegrityError:
        db.session.rollback()
        return error_internal_server("An account already exists with that username.")

@app.route('/accounts/delete', methods=['GET', 'POST'])
def delete_account():
    """
    Delete an account from the database, as well as all messages sent from the account.
    Fails if the account does not exist.

    HTTP request arguments:
        `username`: the username of the desired new account

    Returns: 
        HTTP response object for the client, indicating whether / how the 
        deletion attempt succeeded or failed.
            type: flask.Response
    """
    parsed_json = json.loads(request.data)
    username = parsed_json["username"]

    user = get_user_by_username(username)
    if user:
        db.session.delete(user)
        try:
            db.session.commit()
            return response_ok()
        except exc.SQLAlchemyError:
            return error_internal_server("Internal database error")
    else:
        return error_invalid_params("No account found with username '%s'." % username)

@app.route('/accounts/login', methods=['POST'])
def login():
    """
    Log in a given user. Fails if the account is already logged-in elsewhere, 
    or if it does not exist.

    HTTP request arguments:
        `username`: the username of the account to log in.

    Returns: 
        HTTP response object for the client, indicating whether / how the 
        login attempt succeeded or failed.
            type: flask.Response
    """

    parsed_json = json.loads(request.data)
    username = parsed_json["username"]

    user = get_user_by_username(username)
    if user:
        # Only allow one instance of an account to be logged in at a time.
        if user.logged_in:
        	return error_forbidden("This account is already logged in " \
        		"on another device. Please log out there and try again.")
        else:
        	user.logged_in = True
        	try:
	            db.session.commit()
	            return response_ok()
	        except exc.SQLAlchemyError:
	        	return error_internal_server("Internal database error while logging in")
    else:
        return error_unauthorized("No account found with username '%s'." % username)

@app.route('/accounts/logout', methods=['POST'])
def logout():
    """
    Log out a given user. Fails if the account is not logged in to begin with, 
    or if it does not exist.

    HTTP request arguments:
        `username`: the username of the account to log out.

    Returns: 
        HTTP response object for the client, indicating whether / how the 
        logout attempt succeeded or failed.
            type: flask.Response
    """

    parsed_json = json.loads(request.data)
    username = parsed_json["username"]

    user = get_user_by_username(username)
    if user:
        if user.logged_in:
        	user.logged_in = False
        	try:
	            db.session.commit()
	            return response_ok()
	        except exc.SQLAlchemyError:
	        	return error_internal_server("Internal database error while logging out")
        else:
        	return error_forbidden("This account is not logged in.")
    else:
        return error_unauthorized("No account found with username '%s'." % username)

@app.route('/accounts/search', methods=['POST'])
def search_users():
    """
    Search the database for users with usernames matching a given query string. 
    This search supports variable-length wildcards (signaled by character '*').
    For example, if you query 'a*', usernames 'a', 'aa', and 'abxyz' match, but 
    'ba' does not.

    HTTP request arguments:
        `query`: The query string against which to compare usernames
            type: string

    Returns: 
        HTTP response object for the client. On success, the response includes a
        list of matching usernames encoded in JSON with key `accounts` and status code 200.
        On failure, an error message is passed, and the status code is set appropriately.
            type: flask.Response
    """

    parsed_json = json.loads(request.data)
    query = parsed_json['query']

    # Use SQLAlchemy search syntax
    query = query.replace('*', '%')

    # query the database for matching usernames
    matches = models.User.query.filter( \
    	models.User.username.like(query)).order_by(models.User.username).all()
    match_names = [match.username for match in matches]

    data = {
        "accounts": match_names
    }
    return response_ok(data)


#==================================
## GROUPS

def get_group_by_groupname(groupname):
    """
    Fetch data corresponding to the group with the specified group name 
    from the database.

    Args:
        groupname: the group name of interest
            type: string

    Returns: 
        Object representing data corresponding to the group of interest,
        or None if no matching group was found
            type: models.Group
    """
    return models.Group.query.filter_by(groupname=groupname).first()

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
        return error_unauthorized( \
        	"You can't create a group that doesn't include yourself.")
    users = []
    for username in usernames:
        user = get_user_by_username(username)
        if not user:
            return error_internal_server( \
            	"No account found with username '%s'." % username)
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
        db.session.rollback()
        return error_internal_server("A group already exists with that name.")

def search_by_groupname(fmt_query):
    # query the database for matching groupnames
    matches = models.Group.query.filter(models.Group.groupname.like(fmt_query)) \
    	.order_by(models.Group.groupname).all()
    
    return set(matches)

def search_by_username(fmt_query):
    # query database for matching usernames
    group_set = set()
    matches = models.User.query.filter(models.User.username.like(fmt_query)) \
    	.order_by(models.User.username).all()
    for user in matches:
        group_set |= set(user.groups)

    return group_set

def get_users_by_groupname(groupname):
    group = models.Group.query.filter_by(groupname=groupname).first()
    return group.users

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


#==================================
## MESSAGES 

# Fetch all messages sent to a given user. Unused by the client.
@app.route('/messages/fetch-all', methods=['GET', 'POST'])
def fetch_all_messages():
    parsed_json = json.loads(request.data)
    user = parsed_json["username"]

    if not get_user_by_username(user):
    	return error_internal_server( \
    		"User %s does not exist. Maybe the account was deleted?" % user)

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

    if not get_user_by_username(from_user):
    	return error_internal_server( \
    		"User %s does not exist. Maybe the account was deleted?" % from_user)

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

    if not get_group_by_groupname(from_group):
    	return error_internal_server( \
    		"Group %s does not exist." % from_group)

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

@app.route('/messages/send', methods=['POST'])
def send_message():
    parsed_json = json.loads(request.data)
    sender = parsed_json["sender"]
    to = parsed_json["to"]
    message = parsed_json["message"]

    u = get_user_by_username(to)
    if not u:
    	return error_invalid_params( \
    		"The recipient of this message is not a valid username.")
    u = get_user_by_username(sender)
    if not u:
    	return error_invalid_params( \
    		"The sender of this message is not a valid username.")    

    m = models.Message(body=message, timestamp=datetime.now(),\
        sender_username=sender, to_groupname = None, to_username=to)
    db.session.add(m)

    s = models.Seen(viewer=to, room_user=sender, room_group=None)
    db.session.add(s)

    try:
        db.session.commit()
    except exc.SQLAlchemyError:
    	db.session.rollback()
        return error_internal_server("Internal database error")
    return response_ok()

@app.route('/messages/send-group', methods=['POST'])
def send_message_group():
    parsed_json = json.loads(request.data)
    sender = parsed_json["sender"]
    to_group = parsed_json["to"] # the group name
    message = parsed_json["message"]

    users = get_users_by_groupname(to_group)
    to_group_users = [user.username for user in users]

    m = models.Message(body=message, timestamp=datetime.now(),\
    sender_username=sender, to_groupname=to_group, to_username=None)
    db.session.add(m)
    try:
        db.session.commit()
    except exc.SQLAlchemyError:
    	db.session.rollback()
        return error_internal_server("Internal database error")

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
            	db.session.rollback()
            	return error_internal_server("Internal database error")

    return response_ok()

@app.route('/messages/ack', methods=['GET', 'POST'])
def ack_last_message():
    parsed_json = json.loads(request.data)
    viewer = parsed_json["viewer"]
    room_user = parsed_json.get("room_user")
    room_group = parsed_json.get("room_group")
    last_seen_id = parsed_json["last_seen_id"]

    if not (room_user or room_group):
        return error_invalid_params("Must chat with room or group.")

    msgs = models.Seen.query.filter_by(viewer=viewer)
    msg = msgs.first() 
    if (room_group != None):
        msg = msgs.filter_by(room_group=room_group).first()
    if (room_user != None):
        msg = msgs.filter_by(room_user=room_user).first()
    
    if not msg:
        return error_internal_server("No messages found to ack.")

    msg.last_seen_id = max(last_seen_id, msg.last_seen_id)
    try:
        db.session.commit()
        return response_ok()
    except exc.SQLAlchemyError:
        db.session.rollback()
        return error_internal_server("Internal database error")

