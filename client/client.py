import requestsimport jsonimport threadingimport timeimport sys, termiosfrom Queue import Queue# Server addressSERVER_IP = "http://localhost"SERVER_PORT = "5000"server_url = SERVER_IP + ":" + SERVER_PORT# OptionsCON_WIDTH = 70          # for right-aligning others' messagesPOLL_INTERVAL = 0.5     # frequency for polling server for new messages, in secondsusername = ""logged_in = False# Console commandsCOMMANDS = {    'help': (['help', 'h', '?'], 'Print all commands', []),    'login': (['login', 'l'], 'Log in', ['username']),    'logout': (['logout', 'q'], 'Log out', []),    'new-account': (['newaccount', 'na'], 'Create new account', ['username']),    'delete-account': (['delaccount', 'da'], 'Delete current account', []),    'new-group': (['newgroup', 'ng'], 'Create new chat group', ['groupname', 'user1', 'user2', '...']),    'chat-ind': (['chat', 'c'], 'Chat with user', ['username']),    'chat-group': (['chat', 'cg'], 'Chat with group', ['groupname']),    'list-users': (['listusers', 'lu'], 'List all users', []),    'search-users': (['searchusers', 'su'], 'Search for users by username', ['querystring']),    'list-groups': (['listgroups', 'lg'], 'List all groups', []),    'search-groups': (['searchgroups', 'sg'], 'Search for groups by groupname and included usernames', ['querystring']),    'exit': (['exit'], 'Exit application', []),}def help():    for cmd in sorted(COMMANDS.values()):        print cmd[1]        for c in cmd[0]:            print '  '.join([' ', c, ' '.join('[%s]' % arg for arg in cmd[2])])        print ''# Command handlersdef login(new_username):    global username    global logged_in    if logged_in:        print "You're already logged in as %s; please log out first!" % username    else:        r = requests.post(server_url + "/accounts/login", \            data = json.dumps({'username': new_username}))        if (r.status_code == 200):            username = new_username            logged_in = True            print "Successfully logged in as %s." % username        else:             parsed_json = json.loads(r.text)            message = parsed_json['message']            print "Error: %s" % messagedef create_account(new_username):    if logged_in:        print "You can't create an account while logged in as another user."    else:         r = requests.post(server_url + "/accounts/create", \            data = json.dumps({'username': new_username}))        if r.status_code == 200:            print "Successfully created account \'%s\'." % new_username        else:            parsed_json = json.loads(r.text)            message = parsed_json['message']            print "Error: %s" % messagedef delete_account():    global logged_in    global username    if not logged_in:        print "You can't delete your account when not logged in."    else:        r = requests.post(server_url + "/accounts/delete", \            data = json.dumps({'username': username}))        if r.status_code == 200:            print "Successfully deleted account \'%s\'." % username            username = ""            logged_in = False        else:            parsed_json = json.loads(r.text)            message = parsed_json['message']            print "Error: %s" % message            print "Failed to delete account. Please try again."def logout():    global logged_in    global username    if not logged_in:        print "You're not logged in."    else:        r = requests.post(server_url + "/accounts/logout", \            data = json.dumps({'username': username}))        if r.status_code == 200:            print "Successfully logged out account \'%s\'." % username            username = ""            logged_in = False        else:            parsed_json = json.loads(r.text)            message = parsed_json['message']            print "Error: %s" % message            print "Failed to log out. Please try again."def create_group(groupname, users):    global username    global logged_in    # errors    if not logged_in:        print "You must be logged in to create chat groups."        return     # add current user to user list, if necessary    if username not in users:        users.append(username)    if len(set(users)) < 2:        print "You must invite at least one other user to the group. </3"        return    data = {        'creator' : username,        'groupname' : groupname,        'usernames' : users    }    r = requests.post(server_url + "/groups/create", data = json.dumps(data))    if r.status_code == 200:        print "Successfully created group \'%s\'." % groupname    else:        parsed_json = json.loads(r.text)        message = parsed_json['message']        print "Error: %s" % message# TODO: Return author list for group messages for display purposesdef ack(ids, last_id, room_name, do_group):    data = {        "viewer" : username,        "room_user" : None if do_group else room_name,        "room_group" : room_name if do_group else None,        "last_seen_id" : max(ids)    }    r = requests.post(server_url + '/messages/ack', data = json.dumps(data))    if r.status_code != 200:        parsed_json = json.loads(r.text)        message = parsed_json['message']        print "Error: %s" % messagedef fetch_undelivered_messages(from_name, do_group):    data = {        'to' : username,        'from' : from_name    }    fetch_str = 'fetch-undelivered'    if (do_group):        fetch_str += '-group'    r = requests.post(server_url + '/messages/' + fetch_str, \        data = json.dumps(data))    if r.status_code != 200:        parsed_json = json.loads(r.text)        message = parsed_json['message']        print "Error: %s" % message        return None    else:        parsed_json = json.loads(r.text)        last_id = parsed_json['last_id']        ids = parsed_json['ids']        if (last_id != None) and (len(ids) > 0):            ack(ids, last_id, from_name, do_group)        senders = None        if (do_group):            senders = parsed_json['authors']        return (parsed_json['messages'], senders)# Return True if message was successfully sentdef send_message(to_name, do_group, message):    data = {        'to': to_name,        'sender': username,        'message': message    }    send_str = 'send'    if (do_group):        send_str += '-group'    r = requests.post(server_url + '/messages/' + send_str, \        data = json.dumps(data))    if r.status_code != 200:        parsed_json = json.loads(r.text)        error_message = parsed_json['message']        print "Error: %s" % error_message        if r.status_code == 400:            return False        print "Message failed to send: " + message        retry_str = raw_input("Type y to resend: ")        if (retry_str == "y"):            return send_message(to_name, do_group, message)    return Truedef print_matching_users(query):    r = requests.post(server_url + "/accounts/search", \        data = json.dumps({'query': query}))    if r.status_code != 200:        parsed_json = json.loads(r.text)        error_message = parsed_json['message']        print "Error: %s" % error_message    else:         parsed_json = json.loads(r.text)        results = parsed_json['accounts']        print 'Found %d result(s).' % len(results)        for username in results:            print '  %s' % usernamedef print_all_users():    print_matching_users("*")def print_matching_groups(query):    r = requests.post(server_url + "/groups/search", \        data = json.dumps({'query': query}))    if r.status_code != 200:        parsed_json = json.loads(r.text)        error_message = parsed_json['message']        print "Error: %s" % error_message    else:        parsed_json = json.loads(r.text)                results_by_groupname = parsed_json['groups_by_groupname']        results_by_username = parsed_json['groups_by_username']        if not (results_by_groupname or results_by_username):            print 'No groups match this query.'            return         if results_by_groupname:            print 'Found %d group(s) with matching groupnames.' % len(results_by_groupname)            for groupname in results_by_groupname:                print '  %s' % groupname        if results_by_username:            print 'Found %d group(s) containing matching username(s).' % len(results_by_username)            for groupname in results_by_username:                print '  %s' % groupnamedef print_all_groups():      print_matching_groups('*')# Background daemon for polling for new messagesclass PollMessages(threading.Thread):    def __init__(self, data):        threading.Thread.__init__(self)        self.data = data    def run(self):        do_group = self.data["do_group"]        name = self.data["name"]        q = self.data["q"]        p = self.data["p"]        while(q.empty()):            resp = fetch_undelivered_messages(name, do_group)            if not resp:                p.put(1)                break            (messages, senders) = resp            sender = name            if (len(messages) > 0):                if (senders == None):                    print ("\n[%s]" % name).rjust(CON_WIDTH)                for i in range(0, len(messages)):                    # Logic below used to print the correct sender in a                     # group chat.                    if ((senders != None) and \                      ((i == 0) or \                        (senders[i-1] != senders[i]))):                        print ("%s:" % senders[i]).rjust(CON_WIDTH)                    print messages[i].rjust(CON_WIDTH)            time.sleep(POLL_INTERVAL)        q.get()        returndef chat(name, do_group):    if not logged_in:        print "You must be logged in to chat."        return    EXIT_CHAT = ":q"    print '========================================='    print 'Chat with %s' % name    print '========================================='    quit = False    print "Type %s to leave chat." % EXIT_CHAT    data = {        "name": name,        "do_group": do_group,        "q" : Queue(), # place data in here to kill the polling thread        "p" : Queue(), # place data in here to kill the user-input thread (this)    }    # Spin up background daemon to poll server for new messages    t = PollMessages(data)    t.daemon = True    t.setDaemon(True)    t.start()    time.sleep(1)    while data["p"].empty() and not quit:        send_str = raw_input("")        if (send_str == EXIT_CHAT):            quit = True        else:             # Die if the other user has deleted            quit = not send_message(name, do_group, send_str)    data["q"].put(1)    t.join()    print '========================================='## MENUdef parse_command(command_arr):    incorrect_str = "Incorrect argument count."    if (command_arr[0] in COMMANDS['help'][0]):        if (len(command_arr) != len(COMMANDS['help'][2]) + 1):            print incorrect_str        else:            help()    elif (command_arr[0] in COMMANDS['login'][0]):        if (len(command_arr) != len(COMMANDS['login'][2]) + 1):            print incorrect_str        else:            login(command_arr[1])    elif (command_arr[0] in COMMANDS['logout'][0]):        if (len(command_arr) != len(COMMANDS['logout'][2]) + 1):            print incorrect_str        else:            logout()    elif (command_arr[0] in COMMANDS['new-account'][0]):        if (len(command_arr) != len(COMMANDS['new-account'][2]) + 1):            print incorrect_str        else:            create_account(command_arr[1])    elif (command_arr[0] in COMMANDS['delete-account'][0]):        if (len(command_arr) != len(COMMANDS['delete-account'][2]) + 1):            print incorrect_str        else:            delete_account()    elif (command_arr[0] in COMMANDS['new-group'][0]):        if (len(command_arr) < 3):            # expected arguments: groupname name1 name2 ...            # so, at least one other person in group            print incorrect_str        else:            create_group(command_arr[1], command_arr[2:])    elif (command_arr[0] in COMMANDS['list-users'][0]):        if (len(command_arr) != len(COMMANDS['list-users'][2]) + 1):            print incorrect_str        else:            print_all_users()    elif (command_arr[0] in COMMANDS['search-users'][0]):        if (len(command_arr) != len(COMMANDS['search-users'][2]) + 1):            print incorrect_str        else:            print_matching_users(command_arr[1])    elif (command_arr[0] in COMMANDS['list-groups'][0]):        if (len(command_arr) != len(COMMANDS['list-groups'][2]) + 1):            print incorrect_str        else:            print_all_groups()    elif (command_arr[0] in COMMANDS['search-groups'][0]):        if (len(command_arr) != len(COMMANDS['search-groups'][2]) + 1):            print incorrect_str        else:            print_matching_groups(command_arr[1])    elif (command_arr[0] in COMMANDS['chat-ind'][0]):        if (len(command_arr) != len(COMMANDS['chat-ind'][2]) + 1):            print incorrect_str        else:            chat(command_arr[1], False)    elif (command_arr[0] in COMMANDS['chat-group'][0]):        if (len(command_arr) != len(COMMANDS['chat-group'][2]) + 1):            print incorrect_str        else:            chat(command_arr[1], True)    elif (command_arr[0] in COMMANDS['exit'][0]):        if (len(command_arr) != len(COMMANDS['exit'][2]) + 1):            print incorrect_str        else:            return False    else:         print "What?"    return Trueif __name__ == '__main__':    print "This is CS50."    print "To see available commands, type \'help\'.\n"    loop = True    while loop:        if logged_in:            command_str = "%s > " % username        else:            command_str = "[not logged in] > "        command = raw_input(command_str)        command_arr = command.split()        loop = parse_command(command_arr)