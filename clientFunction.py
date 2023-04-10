import config 
#from serverFunction import *
#import service_pb2 as pb2
#import service_pb2_grpc
import sys
import grpc
import signal
import curses
import time
from menu import menu
import rpc_service_pb2 as pb2
import rpc_service_pb2_grpc
import threading


myname = "" # global variable for the client program to know who I am
mymsgcount = 1 # global variable for the client 

CREATE_ACCOUNT_UI = 1
LOGIN_ACCOUNT_UI = 2
LIST_ACCOUNT_UI = 3
SEND_MESSAGE_UI = 4
DELETE_ACCOUNT_UI = 5
LOGOUT_UI = 6
FETCH_MESSAGE_UI = 7
EXIT_PROGRAM_UI = 8


# visiting all server nodes for requests
# Only the leader will return
def rpc_try_all(chat_request, stubs):

    for s in stubs:
        try:
            response = s.rpc_chat_serve(chat_request)
            # print(tmp)
            if response.status != config.SERVER_ERROR:
                return (response, True)
        except grpc.RpcError as e:
            pass
    return (None, False)


# register a handler for time out
def handler(signum, frame):
    print_red("Server does not respond! The leader died mid way. Try again later!")
    raise Exception("Leader Died Midway Error.")
    

def create_account(stubs):
    """
    User creating an account
    """
    name = input("Input a username with alphabets and numeric of max length {} >> ".format(config.USERNAME_LIMIT)).strip()
    while not name.isalnum() or len(name) > config.USERNAME_LIMIT:
        print("Username contains illegal character or is too long.")
        name = input("Input a username with alphabets and numeric of max length {} >> ".format(config.USERNAME_LIMIT)).strip()

    ### create RPC call:
    request = pb2.ChatRequest()
    request.op = config.CREATE_ACCOUNT
    request.username = name

    # catching time out on server side
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(3)
    try:
        (response, ok) = rpc_try_all(request, stubs)
        signal.alarm(0) # cancel alarm now
    except Exception as error:
        print(error)
        return
        

    if ok:
        #print(response.op, response.status)
        if response.status == config.SUCCESS:
            for msg in response.messages:
                print_green(msg)
            for user in response.usernames:
                print_green(user)
        else:
            for msg in response.messages:
                print_red("Error: "+msg)
    else:
        print_red("Error: Servers don't have a leader.")
    return
  
def get_all_accounts(stubs):
    request = pb2.ChatRequest()
    request.op = config.LIST_ACCOUNT
    request.wildcard = "*"

    # catching time out on server side
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(3)
    try:
        (response, ok) = rpc_try_all(request, stubs)
        signal.alarm(0) # cancel alarm now
    except Exception as error:
        print_red(error)
        return

    return None if response is None else response.usernames

def login_account(stubs):
    """
    User log in an account after creating an account
    It sends a request to server to verify if this account exists
    The server won't store the log in information
    This log in is only for the local program to store the global variable myname
    """
   
    # first acquire all possible accounts
    current_account_names = get_all_accounts(stubs)

    if current_account_names is not None and len(current_account_names) > 0:
        actions = current_account_names
        message = "\nChoose a user account to log in.\n\n"
        name = curses.wrapper(menu, current_account_names, message)
    else:
        actions = ["Back to Previous Page"]
        message = "\nNo Accounts Yet.\nn"
        name = curses.wrapper(menu, current_account_names, message)
        return
        

    #name = input("Input a user name to log in >> ").strip()
    #while not name.isalnum() or len(name)> config.USERNAME_LIMIT:
    #    print("Username contains illegal character or is too long.")
    #    name = input("Input a user name to log in >> ").strip()
    

    ### create RPC call:
    request = pb2.ChatRequest()
    request.op = config.CHECK_ACCOUNT
    request.username = name

    # catching time out on server side
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(3)
    try:
        (response, ok) = rpc_try_all(request, stubs)
        signal.alarm(0) # cancel alarm now
    except Exception as error:
        print(error)
        return

    if ok:
        #print(response.op, response.status)
        if response.status == config.SUCCESS:
            global myname
            myname = name
            print_green("Login success for account {}.".format(myname))
            fetch_message(stubs)
        elif response.status == config.ACCOUNT_NOT_EXIST:
            print_red("Account does not exist.")
    else:
        print_red("Error: Servers don't have a leader.")



def list_account(stubs):
    """
    List account name with wildcard, only * is supported
    """
    msg = input("Input a username search pattern with alphabets, numeric and wildcard * >> ").strip()
    while (not msg.replace("*","").isalnum() and msg != "*"):
        print("Username pattern is illegal.")
        msg = input("Input a username search patter with alphabets, numeric and wildcard * >> ").strip()
    
    request = pb2.ChatRequest()
    request.op = config.LIST_ACCOUNT
    request.wildcard = msg

    # catching time out on server side
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(3)
    try:
        (response, ok) = rpc_try_all(request, stubs)
        signal.alarm(0) # cancel alarm now
    except Exception as error:
        print(error)
        return

    message = ""
    if ok:
        if len(response.usernames) == 0:
            message = "No accounts found."
            print_red(message, wait=False)
        else:
            for user in response.usernames:
                message += "    "+user+"\n"
            message += "All accounts conforming to the pattern listed."
            print_yellow(message, wait=False)
    else:
        message = "Error: Servers don't have a leader."
        print_red(message, wait=False)

    actions = ["Back to Previous Page"]
    message = "\nListing Accounts: \n{}\n\n".format(message)
    curses.wrapper(menu, actions, message)


def send_message(stubs):
    """
    User send message to another user.
    """

    # first acquire all possible accounts
    current_account_names = get_all_accounts(stubs)

    if current_account_names is not None and len(current_account_names) > 0:
        actions = current_account_names
        message = "\nChoose a user account to send a message.\n\n"
        target_name = curses.wrapper(menu, current_account_names, message)
    else:
        actions = ["Back to Previous Page"]
        message = "\nNo Accounts Yet.\nn"
        name = curses.wrapper(menu, current_account_names, message)
        return
        

    #target_name = input("Specify a target name with alphabets and numeric of max length {} >> ".format(config.USERNAME_LIMIT)).strip()
    #while not target_name.isalnum() or len(target_name)> config.USERNAME_LIMIT:
    #    target_name = input("Specify a target name with alphabets and numeric of max length {} >> ".format(config.USERNAME_LIMIT)).strip()
    
    msg = input("Input your message of max length {} characters >> ".format(config.MESSAGE_LIMIT))
    while len(msg) > config.MESSAGE_LIMIT:
        print("Message length longer than {}".format(config.MESSAGE_LIMIT))
        msg = input("Input your message of max length {} characters >> ".format(config.MESSAGE_LIMIT))

    request = pb2.ChatRequest()
    request.op = config.SEND_MESSAGE
    request.username = myname
    request.target_name = target_name
    request.message = msg

    # catching time out on server side
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(3)
    try:
        (response, ok) = rpc_try_all(request, stubs)
        signal.alarm(0) # cancel alarm now
    except Exception as error:
        print(error)
        return

    if ok:
        if response.status == config.SUCCESS:
            print_green("Message sent: "+response.messages[0])
        else:
            print_red("Error: " + response.messages[0])
    else:
        print_red("Error: Servers don't have a leader.")

    

def delete_account(stubs):
    """
    A logged in user delete its account
    This automatically logs out a user
    """
    msg = "\nAre you sure to delete your account?\n\n"
    actions = ["Yes", "No"]
    msg = curses.wrapper(menu, actions, msg)

    #msg = input("Are you sure to delete account {} (Y/N) >> ".format(myname))
    #while msg not in ["Y","N"]:
    #    msg = input("Are you sure to delete account {} (Y/N) >> ".format(myname))

    if msg == "No": return

    request = pb2.ChatRequest()
    request.op = config.DELETE_ACCOUNT
    request.username = myname

    # catching time out on server side
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(3)
    try:
        (response, ok) = rpc_try_all(request, stubs)
        signal.alarm(0) # cancel alarm now
    except Exception as error:
        print(error)
        return

    if ok:
        if response.status == config.SUCCESS:
            print_green("Account {} deleted.".format(myname))
            logout(stubs)
        else:
            print_red("Error: " + response.message[0])
    else:
        print_red("Error: Servers don't have a leader.")


def logout(stubs):
    """
    The server does not need to know a client is logged off.
    Logging off here is only updating the global variable myname to ""
    Return:
        proceed to response: no need to listen to server's response
    """
    global myname
    global mymsgcount
    myname = ""
    mymsgcount = 1
    print("Logged out.")


def fetch_message(stubs):
    """
    The client keeps a counter mymsgcount for fetching through all historical msg.
    When client/server crash, the counter mymsgcount restarts from 0 again. 
    fetch message handles message receives itself.
    return:
        proceed to response: no need to listen to server's response
    """
    global mymsgcount

    request = pb2.ChatRequest()
    request.op = config.FETCH_MESSAGE
    request.username = myname
    request.param_1 = mymsgcount

    # catching time out on server side
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(3)
    try:
        (response, ok) = rpc_try_all(request, stubs)
        signal.alarm(0) # cancel alarm now
    except Exception as error:
        print(error)
        return
    
    if ok:
        message = "\n{}'s new messages\n\n".format(myname)
        if response.status == config.NO_ELEMENT:
            #print_yellow("No new messages.")
            message += "No new messages.\n"
        elif response.status != config.SUCCESS:
            #print_red("Error: " +response.messages[0])
            message += "Error:"+response.messages[0]+"\n"
        else:
            for i in range(len(response.messages)):
                message += "   "+response.usernames[i]+" : "+response.messages[i]+"\n"
                #print_yellow("   " + response.usernames[i]+" : "+response.messages[i])
                mymsgcount += 1

        actions = ["Continue"]
        name = curses.wrapper(menu, actions, message)

    else:
        print_red("Error: Servers don't have a leader.")
                
    
DISPATCH = { CREATE_ACCOUNT_UI: create_account,
             LOGIN_ACCOUNT_UI: login_account,
             LIST_ACCOUNT_UI: list_account,
             SEND_MESSAGE_UI: send_message,
             DELETE_ACCOUNT_UI: delete_account,
             LOGOUT_UI: logout,
             FETCH_MESSAGE_UI: fetch_message}


def print_red(text, wait=True):
    print('\033[0;31m' + text + '\033[0m')
    if wait:time.sleep(2)

def print_green(text, wait=True):
    print('\033[0;32m' + text + '\033[0m')
    if wait:time.sleep(2)

def print_cyan(text, wait=True):
    print('\033[0;34m' + text + '\033[0m')
    if wait:time.sleep(2)

def print_yellow(text, wait=True):
    print('\033[0;33m' + text + '\033[0m')
    if wait:time.sleep(2)
