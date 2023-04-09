import logging
logging.basicConfig(level=logging.DEBUG)

import sys
import grpc
import rpc_service_pb2 as pb2
import rpc_service_pb2_grpc

import threading

import config

def main():
    if len(sys.argv) == 2:
        id = int(sys.argv[1])
    else:
        id = 0
        
    # get ip address and port of the server replica from configuration file
    replica = config.replicas[id]

    try:
        channel = grpc.insecure_channel(replica.ip_addr + ':' + replica.client_port)
        stub = rpc_service_pb2_grpc.ChatServiceStub(channel)
        print(f"Connected with host {replica.ip_addr}, port {replica.client_port}")
    except:
        print("Error: Cannot connect to host {} port {}, try again.".format(replica.ip_addr, replica.client_port))
        sys.exit()
    
    def foo(message):
        request = pb2.ChatRequest()
        request.message = message
        response = stub.rpc_chat_serve(request)
        print(response)
    
    threading.Thread(target=foo, args=("client request 1", )).start()
    threading.Thread(target=foo, args=("client request 2", )).start()
                         
if __name__ == "__main__":
    main()
