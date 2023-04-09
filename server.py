
import logging
logging.basicConfig(level=logging.DEBUG)

from concurrent import futures
import grpc
import rpc_service_pb2_grpc
import rpc_service_pb2

import socket
import sys
import threading
import queue

# import serverFunction

import raft as raft

import config


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
SERVER_ERROR = 190


class ChatServiceServicer(rpc_service_pb2_grpc.ChatServiceServicer):

    """ Customized initialization """
    def my_init(self, replicas, my_id):
        self.lock = threading.Lock()
        self.results = dict()        # stores the response for each client request
        
        # queue of requests that have been commited but not applied yet. 
        self.apply_queue = queue.Queue()

        # create a RAFT server and start it
        self.rf = raft.RaftServiceServicer(replicas, id, self.apply_queue)
        self.rf.my_start()
     

    """ The RPC service provided to the client.
        Input:
            a request (a pb2 object)
        Yield:
            a stream of responses (each a pb2 ojbect)
    """
    def rpc_chat_serve(self, request, context):
        logging.info("Chat: receives: " + request.message)

        # Try to add the request to the log, using the low-level mechanism
        (index, term, is_leader) = self.rf.new_entry(request)

        # If this request cannot be added because this server is not the leader: 
        #   return error message to the client
        if not is_leader:
            response = rpc_service_pb2.ChatResponse(op=request.op)
            response.status = SERVER_ERROR
            response.messages.append("Server is not leader.")
            return response
        
        # Now, we know that the server is the leader:
        # wait until the request is applied
        #   Create an event to indicate whether this request has been applied or not
        self.lock.acquire()
        assert index not in self.results
        self.results[index] = [ threading.Event(), None ]
        self.lock.release()

        logging.info(f"Chat: waiting for event, index={index}")
        self.results[index][0].wait()         # wait for the event
        response = self.results[index][1]     # get the responses
        logging.info(f"Chat: got event, index={index}")
        return response
    

    """ A loop that continuously applies requests that have been commited by RAFT
    """
    def apply_request_loop(self):
        while True:
            log_entry = self.apply_queue.get()
            index = log_entry.index
            request = log_entry.command

            with self.lock:
                # apply request, and (if needed) record results and notify the waiting thread. 
                if index not in self.results:
                    # This case means that the request is not initiated by the current server; 
                    # it is replicated from other servers' logs instead.
                    # So, we don't need to record the result and respond to client. 
                    # We can just apply the request to the state machine
                    logging.info(f"     Apply request index = {index},  message={request.message}")
                    self.apply(request)
                else:
                    # Otherwise, we need to record the results and notify the current server
                    self.results[index][1] = self.apply(request)
                    # set the event to notify the waiting thread
                    self.results[index][0].set()
    

    """ Apply request:
        Return: resopnse to the client 
        ****  must acquire lock before calling  ****
    """
    def apply(self, request):
        assert self.lock.locked()
        res = rpc_service_pb2.ChatResponse()
        res.messages.append( request.message + " (is applied)" )
        return res


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("ERROR: Please use 'python3 server.py id' where id (starting from 0) is the id of the server replica")
        sys.exit()
    
    id = int(sys.argv[1])
    assert 0 <= id < config.n_replicas

    mode = "local"    
    if mode == "local":
        # Local mode:   set the HOST to be 127.0.0.1
        HOST = "127.0.0.1"
        print("Local mode. \n  Client should connect to", HOST)
    else:
        # Network mode:   get the IP address of the server and print it.   
        HOST = "0.0.0.0"
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip_addr = s.getsockname()[0]
        print("Network mode. \n  Server's IP address:", ip_addr) 

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=128))
    servicer = ChatServiceServicer()
    servicer.my_init(config.replicas, id)
    
    threading.Thread(target=servicer.apply_request_loop, args=()).start()

    rpc_service_pb2_grpc.add_ChatServiceServicer_to_server( servicer, server )

    my_ip_addr = config.replicas[id].ip_addr
    my_client_port = config.replicas[id].client_port
    server.add_insecure_port(my_ip_addr + ":" + my_client_port)
    server.start()
    server.wait_for_termination()

