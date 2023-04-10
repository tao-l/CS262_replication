import logging
logging.basicConfig(level=logging.DEBUG)

import sys
import grpc
import rpc_service_pb2 as pb2
import rpc_service_pb2_grpc

import threading

import config
from config import *


# get the ip addresses and ports of all server replicas from the configuration file
replicas  = config.replicas
n_replicas = len(replicas)

stubs = []
for i in range(n_replicas):
    channel = grpc.insecure_channel(replicas[i].ip_addr + ':' + replicas[i].client_port)
    s = rpc_service_pb2_grpc.ChatServiceStub(channel)
    stubs.append(s)

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


def create_account_once(name):
    request = pb2.ChatRequest()
    request.op = CREATE_ACCOUNT
    request.username = name
    (response, ok) = rpc_try_all(request, stubs)
    return response

def test_create_account():
    response = create_account_once("gary")
    print(response.messages[0])
    assert response.status == SUCCESS

    response = create_account_once("gary")
    print(response.messages[0])
    assert response.status == GENERAL_ERROR

    response = create_account_once("gary2")
    print(response.messages[0])
    assert response.status == SUCCESS

    response = create_account_once("aslsdkfjasldkfjsaldkasaaa")
    print(response.messages[0])
    assert response.status == INVALID_USERNAME


def check_account_once(name):
    request = pb2.ChatRequest()
    request.op = CHECK_ACCOUNT
    request.username = name
    (response, ok) = rpc_try_all(request, stubs)
    return response

def test_check_account():
    create_account_once("a new account")
    response = check_account_once("a new account")
    print(response.messages[0])
    assert response.status == SUCCESS

    response = check_account_once("non-existing account")
    print(response.messages[0])
    assert response.status == ACCOUNT_NOT_EXIST


def list_account_once(wildcard):
    request = pb2.ChatRequest()
    request.op = LIST_ACCOUNT
    request.wildcard = wildcard
    (response, ok) = rpc_try_all(request, stubs)
    return response

def test_list_account():
    response = list_account_once("ga")
    assert len(response.usernames) == 0

    response = list_account_once("*")
    for user in response.usernames:
        print(user)
                         
if __name__ == "__main__":
    # test_create_account()
    test_check_account()
    test_list_account()
