import logging
logging.basicConfig(level=logging.DEBUG)

import sys
import grpc
import rpc_service_pb2 as pb2
import rpc_service_pb2_grpc

import threading

import config



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


def main():
    # get the ip addresses and ports of all server replicas from the configuration file
    replicas  = config.replicas
    n_replicas = len(replicas)

    stubs = []
    for i in range(n_replicas):
        channel = grpc.insecure_channel(replicas[i].ip_addr + ':' + replicas[i].client_port)
        s = rpc_service_pb2_grpc.ChatServiceStub(channel)
        stubs.append(s)

    
    ### Example RPC call:
    request = pb2.ChatRequest()
    request.op = config.LIST_ACCOUNT
    request.message = "this is request message"
    (response, ok) = rpc_try_all(request, stubs)
    print(ok)
    if ok:
        print(response.op, response.status)
        for msg in response.messages:
            print(msg)
        for user in response.usernames:
            print(user)

                         
if __name__ == "__main__":
    main()
