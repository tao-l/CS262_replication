from serverFunction import *
import service_pb2 as pb2
import service_pb2_grpc

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


def create_account(stub):
    """
    User creating an account
    """
    name = input("Input a username with alphabets and numeric of max length {} >> ".format(USERNAME_LIMIT)).strip()
    while not name.isalnum() or len(name) > USERNAME_LIMIT:
        print("Username contains illegal character or is too long.")
        name = input("Input a username with alphabets and numeric of max length {} >> ".format(USERNAME_LIMIT)).strip()
    
    user = pb2.User()
    user.username = name
    response = stub.rpc_create_account(user)
    #print("length of response create account", response.ByteSize())
    if response.status == SUCCESS:
        print_green(response.message)
    else:
        print_red("Error: " + response.message)
    return

def login_account(stub):
    """
    User log in an account after creating an account
    It sends a request to server to verify if this account exists
    The server won't store the log in information
    This log in is only for the local program to store the global variable myname
    """
    name = input("Input a user name to log in >> ").strip()
    while not name.isalnum() or len(name)> USERNAME_LIMIT:
        print("Username contains illegal character or is too long.")
        name = input("Input a user name to log in >> ").strip()
    

    user = pb2.User()
    user.username = name
    response = stub.rpc_check_account(user)
    if response.status == SUCCESS:
        global myname
        myname = name
        print_green("Login success for account {}.".format(myname))
        fetch_message(stub)
    elif response.status == ACCOUNT_NOT_EXIST:
        print_red("Account does not exist.")


def list_account(stub):
    """
    List account name with wildcard, only * is supported
    """
    msg = input("Input a username search pattern with alphabets, numeric and wildcard * >> ").strip()
    while (not msg.replace("*","").isalnum() and msg != "*"):
        print("Username pattern is illegal.")
        msg = input("Input a username search patter with alphabets, numeric and wildcard * >> ").strip()

    wildcard = pb2.Wildcard()
    wildcard.wildcard = msg
    response_len = 0
    for user in stub.rpc_list_account(wildcard):
        response_len += 1
        print_yellow("   " + user.username)

    if not response_len:
        print("No accounts found.")
    else:
        print("All accounts conforming with the pattern listed.")


def send_message(stub):
    """
    User send message to another user.
    """
    target_name = input("Specify a target name with alphabets and numeric of max length {} >> ".format(USERNAME_LIMIT)).strip()
    while not target_name.isalnum() or len(target_name)> USERNAME_LIMIT:
        target_name = input("Specify a target name with alphabets and numeric of max length {} >> ".format(USERNAME_LIMIT)).strip()
    
    msg = input("Input your message of max length {} characters >> ".format(MESSAGE_LIMIT))
    while len(msg) > MESSAGE_LIMIT:
        print("Message length longer than {}".format(MESSAGE_LIMIT))
        msg = input("Input your message of max length {} characters >> ".format(MESSAGE_LIMIT))

    chat_msg = pb2.ChatMessage() 
    chat_msg.username = myname
    chat_msg.target_name = target_name
    chat_msg.message = msg
    response = stub.rpc_send_message(chat_msg)
    if response.status == SUCCESS:
        print_green(response.message)
    else:
        print_red("Error: " + response.message)
    

def delete_account(stub):
    """
    A logged in user delete its account
    This automatically logs out a user
    """
    msg = input("Are you sure to delete account {} (Y/N) >> ".format(myname))
    while msg not in ["Y","N"]:
        msg = input("Are you sure to delete account {} (Y/N) >> ".format(myname))

    if msg == "N": return

    user = pb2.User()
    user.username = myname
    response = stub.rpc_delete_account(user)
    # print(response.message)
    if response.status == SUCCESS:
        print_green("Account {} deleted.".format(myname))
        logout(stub)
    else:
        print_red("Error: " + response.message)


def logout(stub):
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


def fetch_message(stub):
    """
    The client keeps a counter mymsgcount for fetching through all historical msg.
    When client/server crash, the counter mymsgcount restarts from 0 again. 
    fetch message handles message receives itself.
    return:
        proceed to response: no need to listen to server's response
    """
    global mymsgcount
    fetch_request = pb2.FetchRequest()
    fetch_request.msg_id = mymsgcount
    fetch_request.username = myname
    for chat_msgs in stub.rpc_fetch_message(fetch_request):
        if chat_msgs.status in (NO_NEXT_ELEMENT, NEXT_ELEMENT_EXIST):
            print("Message:")
            print_yellow("  " + chat_msgs.username + " : " + chat_msgs.message)
            mymsgcount += 1
        elif chat_msgs.status == NO_ELEMENT:
            print("No new messages.")
        else:
            print_red("Error: " + chat_msgs.message)
        
    
DISPATCH = { CREATE_ACCOUNT_UI: create_account,
             LOGIN_ACCOUNT_UI: login_account,
             LIST_ACCOUNT_UI: list_account,
             SEND_MESSAGE_UI: send_message,
             DELETE_ACCOUNT_UI: delete_account,
             LOGOUT_UI: logout,
             FETCH_MESSAGE_UI: fetch_message}


def print_red(text):
    print('\033[0;31m' + text + '\033[0m')

def print_green(text):
    print('\033[0;32m' + text + '\033[0m')

def print_cyan(text):
    print('\033[0;34m' + text + '\033[0m')

def print_yellow(text):
    print('\033[0;33m' + text + '\033[0m')
