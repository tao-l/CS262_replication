from concurrent import futures
import socket
import sys
import logging

import grpc
import service_pb2_grpc
import serverFunction

PORT = "23333"
    

if __name__ == "__main__":
    logging.basicConfig()
    
    if len(sys.argv) > 2:
        print("ERROR: Please use 'python server.py local' for running locally or 'python server.py' for network mode ")
        sys.exit()

    mode = "network"
    if len(sys.argv) == 2:
        if sys.argv[1].lower() ==  "local":
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
    service_pb2_grpc.add_ChatRoomServicer_to_server(
        serverFunction.ChatRoomServicer(),
        server
    )
    server.add_insecure_port(HOST + ":"+PORT)
    server.start()
    server.wait_for_termination()

