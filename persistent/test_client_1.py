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
    for i in range(len(stubs)):
        try:
            print(f"Trying server [{i}]")
            response = stubs[i].rpc_chat_serve(chat_request)
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
    return rpc_try_all(request, stubs)

def delete_account_once(name):
    request = pb2.ChatRequest()
    request.op = DELETE_ACCOUNT
    request.username = name
    return rpc_try_all(request, stubs)


def test_create_and_delete_account():
    # test create_account
    (response, ok) = create_account_once("gary")
    print(response.messages[0])

    (response, ok) = create_account_once("gary")
    print(response.messages[0])
    assert response.status == GENERAL_ERROR

    (response, ok) = create_account_once("gary2")
    print(response.messages[0])

    (response, ok) = create_account_once("aslsdkfjasldkfjsaldkasaaa")
    print(response.messages[0])
    assert response.status == INVALID_USERNAME

    # test delete_account
    (response, ok) = delete_account_once("no such user")
    print(response.messages[0])
    assert response.status == ACCOUNT_NOT_EXIST

    (response, ok) = delete_account_once("gary")
    print(response.messages[0])
    (response, ok) = check_account_once("gary")
    assert response.status == ACCOUNT_NOT_EXIST


def check_account_once(name):
    request = pb2.ChatRequest()
    request.op = CHECK_ACCOUNT
    request.username = name
    return rpc_try_all(request, stubs)

def test_check_account():
    create_account_once("a new account")
    (response, ok) = check_account_once("a new account")
    print(response.messages[0])
    assert response.status == SUCCESS

    (response, ok) = check_account_once("non-existing account")
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

def send_message_once(username, target_name, message):
    request = pb2.ChatRequest()
    request.op = SEND_MESSAGE
    request.username = username 
    request.target_name = target_name
    request.message = message
    return rpc_try_all(request, stubs)

def fetch_message_once(username, msg_id):
    request = pb2.ChatRequest()
    request.op = FETCH_MESSAGE
    request.username = username 
    request.param_1 = msg_id
    return rpc_try_all(request, stubs)

def test_send_and_fetch_message():
    # First, create two accounts
    create_account_once("gary")
    create_account_once("gary2")

    # Then, test send_messages
    (response, ok) = send_message_once("gary", "gary", "gary to gary message")
    print(response.messages[0])
    assert response.status == SUCCESS

    (response, ok) = send_message_once("gary_no", "gary2", "2nd message")
    print(response.messages[0])
    assert response.status == ACCOUNT_NOT_EXIST

    (response, ok) = send_message_once("gary", "gary_no", "3rd message")
    print(response.messages[0])
    assert response.status == ACCOUNT_NOT_EXIST

    (response, ok) = send_message_once("gary2", "gary", "4th message")
    print(response.messages[0])
    assert response.status == SUCCESS

    (response, ok) = send_message_once("gary", "gary2", "5th message")
    print(response.messages[0])
    assert response.status == SUCCESS

    # Then, test fetch_messages
    (response, ok) = fetch_message_once("no such user", 1)
    print(response.messages[0])
    assert response.status == ACCOUNT_NOT_EXIST

    (response, ok) = fetch_message_once("gary", 0)
    print(response.messages[0])  # this should print "msg_id < 1"

    (response, ok) = fetch_message_once("gary", 2)
    print(response.messages)

    (response, ok) = fetch_message_once("gary", 100)
    print(response.messages)   # this shoudl print "msg_id > total number of messages"
    
    (response, ok) = fetch_message_once("gary2", 1)
    print(response.messages)

    delete_account_once("gary2")
    create_account_once("gary2")
    (response, ok) = fetch_message_once("gary2", 1)
    print(response.messages)
    assert len(response.usernames) == 0  


if __name__ == "__main__":
    test_create_and_delete_account()
    test_check_account()
    test_list_account()
    test_send_and_fetch_message()
