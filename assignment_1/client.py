import logging
import sys
import grpc
import service_pb2 as pb2
import service_pb2_grpc
import clientFunction
from clientFunction import *

HOST_PORT = "23333"

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

def handle_client_ui():
    """
    Catching illegal client actions before sending commands in to server
    """
    # get user input in command line
    menu_number = user_menu()
    # make sure user login or create account before doing anything else
    while clientFunction.myname == "" and menu_number not in [LIST_ACCOUNT_UI, LOGIN_ACCOUNT_UI, EXIT_PROGRAM_UI, CREATE_ACCOUNT_UI]:
        print("Please log in or create account first before doing other operations.")
        menu_number = user_menu()
    
    # no creating account when logged in
    while clientFunction.myname != "" and menu_number == CREATE_ACCOUNT_UI:
        print("Please log out to create a new account")
        menu_number = user_menu()

    # no double log in
    while clientFunction.myname != "" and menu_number == LOGIN_ACCOUNT_UI:
        print("Please log out to re login. ")
        menu_number = user_menu()

    # If client exits, no longer needs to tell the server to log off
    if menu_number == EXIT_PROGRAM_UI:
        sys.exit()

    return menu_number




def main():
    if len(sys.argv) != 2:
        print("ERROR: Please use python client.py <host ip>. Port is fixed to 23333")
        sys.exit()
    
    # python client.py host_ip
    # get ip address and ports from command line 
    host_ip = str(sys.argv[1])

    try:
        channel = grpc.insecure_channel(host_ip+':'+HOST_PORT)
        stub = service_pb2_grpc.ChatRoomStub(channel)
    except:
        print("Error: Cannot connect to host {} port {}, try again.".format(host_ip, HOST_PORT))
        sys.exit()

    while True: 
        menu_number = handle_client_ui() 
        
        try:
            DISPATCH[menu_number](stub)
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
