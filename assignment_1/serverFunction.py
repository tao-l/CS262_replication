import service_pb2 as pb2
import service_pb2_grpc

import fnmatch
import threading


USERNAME_LIMIT = 20
MESSAGE_LIMIT = 500

SUCCESS = 0
# status codes used when returning a stream of responses. 
NO_ELEMENT = 1
NO_NEXT_ELEMENT = 2
NEXT_ELEMENT_EXIST = 3


 # error codes: range in [100, 199]
INVALID_USERNAME = 101
ACCOUNT_NOT_EXIST = 102
MESSAGE_TOO_LONG = 103
MESSAGE_ID_TOO_LARGE = 104
GENERAL_ERROR = 199


# A data structure shared by all server threads, including: 
#    - a list of all existing accounts/users (identified by their usernames) 
#    - a dictionary mapping users to the set of messages they received.
#      Specifically, messages[user_a] is a list of (user, message) pairs
#      recoding the messages user_a received (and from which user):  
#          messages[user_a] = [ (user_1, message_1), (user_2, message_2), ..., ] 
#    - a lock for the shared data structure. 
class SharedData():
    def __init__(self):
        self.accounts = []
        self.messages = {}
        self.lock = threading.Lock()

shared_data = SharedData()


class ChatRoomServicer(service_pb2_grpc.ChatRoomServicer):
#  The followings are the server's functions.
#  Each function takes a request (a pb2 bject) as input,
#  and returns a response (also a pb2 ojbect)

    def rpc_create_account(self, request, context):
        """ Create account with username [request.username].
            Respond error message if the account cannot be created.
            Parameters:
                user: a service_pb2.User
                context: grpc.ServicerContext 
            Return:
                service_pb2.GeneralResponse  
        """
        print("length of request create account", request.ByteSize())
        username = request.username

        if len(username) > USERNAME_LIMIT:
            response = pb2.GeneralResponse(status=INVALID_USERNAME, message="Username too long.")
            return response
        
        print("create_account: waiting for lock....")
        shared_data.lock.acquire()
        print("create_account: acquired lock.")
        try:  
            if username in shared_data.accounts:
                response = pb2.GeneralResponse(status=GENERAL_ERROR, message=f"User [{username}] already exists!  Pick a different username.")
                print("    create_account: fail.")
            else:
                # Add the user to the account list.
                shared_data.accounts.append(username)
                # Initialize the user's message list to be empty.
                shared_data.messages[username] = []

                response = pb2.GeneralResponse(status=SUCCESS, message=f"Account [{username}] created successfully.  Please log in.")
                print("    create_account: success.")
        finally:
            shared_data.lock.release()
            print("create_account: released lock.")
        
        print("length of response create account", response.ByteSize())
        return response


    def rpc_check_account(self, request, context):
        """ Checks whether the account [request.username] exists in e account list. 
            Respond error message if the account cannot be created.
            Parameters:
                request: a service_pb2.User
                context: grpc.ServicerContext 
            Return:
                service_pb2.GeneralResponse  
        """
        print("length of request check account", request.ByteSize())
        response = pb2.GeneralResponse()
        if request.username in shared_data.accounts:
            response.status = SUCCESS
            response.message = "Account exists."
        else:
            response.status = ACCOUNT_NOT_EXIST
            response.message ="Account does not exist."
        print("length of response check account", response.ByteSize())
        return response


    def rpc_list_account(self, request, context):

        """ - List accounts that match with the wildcard in [request.wildcard].
            - Return a list of those accounts in a stream of users.
            Parameters:
                request: a service_pb2.Wildcard
            Return:
                users: a stream of service_pb2.User
        """
        print("length of request list account", request.ByteSize())
        wildcard = request.wildcard
        for username in shared_data.accounts:
            if fnmatch.fnmatch(username, wildcard):
                response = pb2.User(username=username)
                print("length of response list account for one account", response.ByteSize())
                yield response
    

    def rpc_delete_account(self, request, context):
        """ Delete the account with [request.username].
            All the messages received by this account are discarded (including undelivered ones). 
            Parameters:
                request: a service_pb2.User
            Return:
                service_pb2.GeneralResponse  
        """
        print("length of request delete account", request.ByteSize())
        username = request.username
        response = pb2.GeneralResponse()
        
        print("delete_account: waiting for lock...")
        shared_data.lock.acquire()
        print("delete_account: acquired lock.")    
        try:
            if username not in shared_data.accounts:
                response.status = ACCOUNT_NOT_EXIST
                response.message = f"User [{username}] does not exist!"
            else:
                # Remove the user from the account list
                shared_data.accounts.remove(username)
                # Remove the user's message list.
                shared_data.messages.pop(username)
                response.status = SUCCESS
                response.message = f"Account [{username}] deleted.  All received messages are discarded."
        finally:
            shared_data.lock.release()
            print("delete_account: released lock.")
        
        print("length of response delete account", response.ByteSize())
        return response


    def rpc_send_message(self, request, context):
        """ Send a message from [request.username] to [request.target_name]: 
            - If [request.username] or [request.target_name] does not exist, return error
            - If message is too long, return error
            - Otherwise, update shared_data.messages, return SUCCESS
            Parameters:
                request: a service_pb2.ChatMessage
            Return:
                service_pb2.GeneralResponse  
        """
        print("length of request send message", request.ByteSize())
        response = pb2.GeneralResponse()
        username = request.username
        target_name = request.target_name
        msg = request.message

        if len(msg) > MESSAGE_LIMIT:
            request.status = MESSAGE_TOO_LONG
            response.message = f"Message longer than {MESSAGE_LIMIT}, cannot be sent!"
            print("length of response send message", response.ByteSize())
            return response

        print("send_messgage: waiting for lock...")
        shared_data.lock.acquire()
        print("send_message: acquired lock. ")
        try:
            if username not in shared_data.accounts:
                response.status = ACCOUNT_NOT_EXIST
                response.message = f"Your account [{username}] does not exist!"
            elif target_name not in shared_data.accounts:
                response.status = ACCOUNT_NOT_EXIST
                response.message = f"Target user [{target_name}] does not exist!"
            else:
                # add the pair (username, message) to the target user's message list
                shared_data.messages[target_name].append( (username, msg) )
                response.status = SUCCESS
                response.message = "Message sent succesfully."
        finally:
            shared_data.lock.release()
            print("send_message: released lock. ")
        
        print("length of response send message", response.ByteSize())
        return response


    def rpc_fetch_message(self, request, context):
        """ Client fetches message sent to the user [request.username].
            Client specifies a [msg_id] in [request.status]: 
            Server tries to return all the messages sent to the user starting from the (msg_id)-th one:   
            - If the client's username does not exist, return error. 
            - If [msg_id] < 1, return error. 
            - If [msg_id] is larger than the number of messages the client received, return NO_ELEMENT
            - Otherwise, return a stream of responses, where each response includes 
                * the message in [response.message]
                * the user who sent this message in [response.username]
                * and specify whether there are more responses in [response.status]:
                  - if there are, [response.status] = NEXT_ELEMENT_EXIST
                  - if not, [response.status] = NO_NEXT_ELEMENT
            Parameters:
                request: service_pb2.FetchRequest
            Return:
                chat messages: a stream of service_pb2.ChatMessage
        """
        print("length of request fetch message", request.ByteSize())
        username = request.username
        msg_id = request.msg_id
        responses = [] 

        if msg_id < 1:
            response = pb2.ChatMessage()
            response.status = GENERAL_ERROR
            response.message = "Message id < 1"
            responses = [response]
        else: 
            print("fetch_messgage: waiting for lock...")
            shared_data.lock.acquire()
            print("fetch_message: acquired lock. ")

            if username not in shared_data.accounts:
                response = pb2.ChatMessage()
                response.status = ACCOUNT_NOT_EXIST
                response.message = f"Your account [{username}] does not exist!"
                responses = [response]

            else:                                
                total_msg = len(shared_data.messages[username])
                if msg_id > total_msg:
                    response = pb2.ChatMessage()
                    response.status = NO_ELEMENT
                    response.message = f"Message id {msg_id} > total number of messages {total_msg}"
                    responses = [response]
                    
                for i in range(msg_id-1, total_msg):
                    (from_which_user, message) = shared_data.messages[username][i]
                    response = pb2.ChatMessage()
                    response.message = message 
                    response.username = from_which_user
                    if i == total_msg - 1:
                        response.status = NO_NEXT_ELEMENT
                    else:
                        response.status = NEXT_ELEMENT_EXIST
                    responses.append(response)

            shared_data.lock.release()
            print("fetch_message: released lock. ")
        
        assert len(responses) > 0
        for res in responses:
            print("length of response fetch message for one message", res.ByteSize())
            yield res

