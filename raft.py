""" The RAFT algorithm: used to maintain a consistent log among the replicas
"""

import logging
logging.basicConfig(level=logging.DEBUG)

import raft_service_pb2
import raft_service_pb2_grpc
import grpc

import threading
import queue
import random

from time import sleep
import config

class LogEntry:
    def __init__(self, term, index, command):
        self.term = term
        self.index = index
        self.command = command

Follower = 0
Candidate = 1
Leader = 2

class RaftServiceServicer(raft_service_pb2_grpc.RaftServiceServicer):

    """" Initialization of a RAFT server:
         - Input:
             replicas    : List of the addresses and ports of all replicas
             my_id       : The id of the current server replica
             apply_queue : Given by the High-layer server. 
                           RAFT server puts to this queue log entries that have been commited.
                           High-layer server will pick entires from this queue to execute. 
    """
    def __init__(self, replicas, my_id, apply_queue):
        super().__init__()

        self.lock = threading.Lock()
        self.apply_queue = apply_queue  

        ## Persistent states: 
        self.current_term = 0
        self.voted_for = None
        self.logs = [LogEntry(0, 0, None)]  # (index of the first "real" log entry is 1)

        ## Volatile states: 
        self.commit_index = 0  # index of highest log entry known to be committed
        self.last_applied = 0  # index of the highest log entry applied to state machine
        
        self.state = Follower
        if my_id == 0:
            self.state = Leader

        ## Set up information for other replicas
        self.my_id = my_id
        self.n_replicas = len(replicas)     # number of replicas
        self.replica_stubs = []
        for i in range(self.n_replicas):
            if (i != my_id):
                channel = grpc.insecure_channel(replicas[i].ip_addr + ':' + replicas[i].raft_port)
                s = raft_service_pb2_grpc.RaftServiceStub(channel)
                self.replica_stubs.append(s)
            else:
                self.replica_stubs.append(None)
        
        self.match_index = [0 for i in range(self.n_replicas)]
        self.next_index = None


        self.even_queue = queue.Queue()
        self.heard_heartbeat = False
        self.heard_grant_vote = False

        # init done, run the main loop
        threading.Thread(target=self.main_loop, args=()).start()
    

    def get_last_index(self):
        return len(self.logs) - 1


    def rpc_append_entries(self, AE_request, context):
        logging.info(f"  Raft [{self.my_id}] - AE - receives: " + AE_request.message)
        self.heard_heartbeat = True
        return raft_service_pb2.AE_Response()
    

    """ This function is called by the upper-layer server
        when it receives client request.
        This function puts the request (command) to the RAFT server's log
        and replicating to other RAFT servers. 
        - Input: 
            command   :  chat_service_pb2.Request object
        - Return: (index, term, is_leader):
            index     :  index of the command in the log if the command is committed
            term      :  current term
            is_leader :  whether this RAFT server is the current leader.
                         If no, this command is not added to the log. 
    """
    def new_entry(self, command):
        logging.info(f"  Raft [{self.my_id}] - new entry: " + command.message)
        
        try:
            self.lock.acquire()

            if self.state != Leader:
                logging.info(f"      Raft [{self.my_id}]: not leader, cannot add entry")
                return (-1, self.current_term, False)
            
            term = self.current_term
            index = self.get_last_index() + 1
            self.logs.append( LogEntry(term, index, command) )
            logging.info(f"  Raft [{self.my_id}] adds entry {term, index} to log")
            return (index, term, True)
        
        finally:
            self.lock.release()
    

    """ Call the append_entries RPC of all other RAFT servers
        Lock must be held before calling
    """
    def broadcast_append_entries(self):
        logging.debug(f"  RAFT [{self.my_id}] - broadcast:")
        assert self.lock.locked()
        if self.state != Leader:
            return
        
        for i in range(self.n_replicas):
            if i != self.my_id:
                try:
                    message = f"from {self.my_id} to {i} broadcast"
                    ae_request = raft_service_pb2.AE_Request(message=message)
                    ae_response = self.replica_stubs[i].rpc_append_entries(ae_request)
                except grpc.RpcError as e:
                    # print(e.details())
                    pass
        self.commit_index = self.get_last_index()
        threading.Thread(target=self.apply_logs, args=()).start()
    

    """ 'Apply' the commited logs:
        namely, put the commited log entries to apply_queue
    """
    def apply_logs(self):
        with self.lock:
            for i in range(self.last_applied+1, self.commit_index+1):
                self.apply_queue.put(self.logs[i])
                self.last_applied = i
    
    def new_entry_tmp(self, command):
        logging.info(f"  Raft [{self.my_id}] - new entry: " + command.message)
        
        self.lock.acquire()
        term = self.current_term
        index = len(self.logs)
        self.logs.append( LogEntry(term, index, command) )
        logging.info(f"  Raft [{self.my_id}] adds entry {term, index} to log")
        self.lock.release()

        is_leader = True
        
        def put_command_later(t):
            sleep(t)
            self.lock.acquire()
            self.apply_queue.put(self.logs[index])
            self.lock.release()
        
        threading.Thread(target=put_command_later, args=(random.random(),)).start()

        for i in range(self.n_replicas):
            if i != self.my_id:
                try:
                    message = f"from {self.my_id} to {i} '{command.message}'"
                    ae_request = raft_service_pb2.AE_Request(message=message)
                    ae_response = self.replica_stubs[i].rpc_append_entries(ae_request)
                except grpc.RpcError as e:
                    print(e.details())
        
        return (index, term, is_leader)
    

    def convert_to_candidate(self):
        logging.info(f"  Raft [{self.my_id}] - convert to candidate")
        with self.lock:
            if self.state != Follower:
                return

    # Reset event queue
    # lock must be held before calling this function
    # def reset_event_queue(self):
    #     assert self.lock.locked()
    #    self.event_queue = queue.Queue()


    def main_loop(self):
        while True:
            # print(self.state, self.lock.locked())
            state = self.state
            if state == Leader:
                # sleep(config.leader_broadcast_interval / 1000)
                sleep(1)
                with self.lock: 
                    self.broadcast_append_entries()

            elif state == Follower:
                sleep(2)
                with self.lock:
                    to_convert_to_candidate =  (not self.heard_heartbeat) and (not self.heard_grant_vote)
                    self.heard_heartbeat = False
                    self.heard_grant_vote = False
                if to_convert_to_candidate:
                    self.convert_to_candidate()
            
            elif state == Candidate:
                


