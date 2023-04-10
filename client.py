import logging
import sys
import grpc
import config
import curses
from menu import menu
import threading
import clientFunction
import rpc_service_pb2_grpc
from clientFunction import *

HOST_PORT = "23333"
logging.basicConfig(level=logging.DEBUG)

def user_menu():
    """
    User Terminal Console
    It will keep prompting user for function number until a valid one
    """
    print('''
    Current user: {} \n
        Type the number of a function:
        (1) Create Account
        (2) Login to Account
        (3) List Accounts
        (4) Send a Message
        (5) Delete Account
        (6) Logout
        (7) Fetch Messages
        (8) Exit Program
    '''.format(clientFunction.myname))
    command = input('Input a number of the function >> ').strip()
    while command not in [str(i) for i in range(1,9)]:
        command = input('Input a number of the function >> ').strip()
    return int(command)

UI_CONVERT = {
        "Create Account":1,
        "Login to Account": 2,
        "List Accounts": 3,
        "Send a Message": 4,
        "Delete Account": 5,
        "Logout": 6,
        "Fetch Messages": 7,
        "Exit Program": 8
    }

def handle_client_ui():
    """
    Catching illegal client actions before sending commands in to server
    """
    if clientFunction.myname =="":
        actions = ["Create Account", "Login to Account", "List Accounts", "Exit Program"]
        message = "\nWelcome to messenger! What would you like to do?\n\n"
    else:
        actions = ["List Accounts", "Send a Message", "Delete Account", "Logout", "Fetch Messages", "Exit Program"]
        message = "\n {}'s Account.\n\n".format(clientFunction.myname)

    menu_number = UI_CONVERT[curses.wrapper(menu, actions, message)]

    # get user input in command line
    # menu_number = user_menu()
    # make sure user login or create account before doing anything else
    # while clientFunction.myname == "" and menu_number not in [LIST_ACCOUNT_UI, LOGIN_ACCOUNT_UI, EXIT_PROGRAM_UI, CREATE_ACCOUNT_UI]:
    # print("Please log in or create account first before doing other operations.")
    #    menu_number = user_menu()
    
    # no creating account when logged in
    # while clientFunction.myname != "" and menu_number == CREATE_ACCOUNT_UI:
    #    print("Please log out to create a new account")
    #    menu_number = user_menu()

    # no double log in
    # while clientFunction.myname != "" and menu_number == LOGIN_ACCOUNT_UI:
    #    print("Please log out to re login. ")
    #    menu_number = user_menu()

    # If client exits, no longer needs to tell the server to log off
    if menu_number == EXIT_PROGRAM_UI:
        sys.exit()

    return menu_number


def main():
    # get the ip addresses and ports of all server replicas from the configuration file
    replicas  = config.replicas
    n_replicas = len(replicas)

    stubs = []
    for i in range(n_replicas):
        channel = grpc.insecure_channel(replicas[i].ip_addr + ':' + replicas[i].client_port)
        s = rpc_service_pb2_grpc.ChatServiceStub(channel)
        stubs.append(s)


    while True: 
        menu_number = handle_client_ui()
        
        try:
            DISPATCH[menu_number](stubs)
        except grpc.RpcError as e:
            print(e.details())
            status_code = e.code()
            print(status_code.name)
            print(status_code.value)
            if grpc.StatusCode.INVALID_ARGUMENT == status_code:
                print("Invalid argument passed to gRPC. Modify code!")
            elif grpc.StatusCode.UNAVAILABLE == status_code:
                print("Server down. Contact the server admin to restart.")
                return
                #sys.exit()
                         
if __name__ == "__main__":
    logging.basicConfig()
    main()
