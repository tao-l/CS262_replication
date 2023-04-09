""" The RAFT algorithm: used to maintain a consistent log among the replicas
"""
import logging
logging.basicConfig(level=logging.DEBUG)

import grpc
import rpc_service_pb2
import rpc_service_pb2_grpc

import threading
import queue
import random

from time import sleep
import config

Follower = 0
Candidate = 1
Leader = 2

class RaftServiceServicer(rpc_service_pb2_grpc.RaftServiceServicer):

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
        dummy_command = rpc_service_pb2.ChatRequest()
        self.logs = [rpc_service_pb2.LogEntry(term=0, index=0, command=dummy_command)]
        # (index of the first "real" log entry is 1)

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
                s = rpc_service_pb2_grpc.RaftServiceStub(channel)
                self.replica_stubs.append(s)
            else:
                self.replica_stubs.append(None)
        
        # Leader's states: reinitialized after election
        self.match_index = None
        self.next_index = None

        # events: used to notify the main loop
        self.heard_heartbeat = False
        self.grant_vote = False
        self.received_majority_vote = threading.Event()

        # init done, run the main loop
        threading.Thread(target=self.main_loop, args=()).start()
    

    """ Get the index of the last entry in the log """
    def get_last_index(self):
        return len(self.logs) - 1


    def rpc_append_entries(self, AE_request, context):
        logging.info(f"  RAFT [{self.my_id}] - AE - receives: " + AE_request.message)
        self.heard_heartbeat = True
        if self.my_id == 1:
            with self.lock:
                self.convert_to_follower(100)
        return raft_service_pb2.AE_Response()
    

    """ When receiving a new client request, the upper-layer server calls
        this function to try to add the request (command) to RAFT's log. 
        RAFT varifies whether this server is the current Leader,
        and if yes, replicates the command to other RAFT servers. 
        - Input: 
            command   :  rpc_service_pb2.ChatRequest object
        - Return: (index, term, is_leader):
            index     :  index of the command in the log if the command is committed
            term      :  current term
            is_leader :  whether this server is the current Leader.
                         If no, this command is not added to the log. 
    """
    def new_entry(self, command):
        logging.info(f"  RAFT [{self.my_id}] - new entry: " + command.message)   
        with self.lock: 
            if self.state != Leader:
                logging.info(f"      RAFT [{self.my_id}]: not leader, cannot add entry")
                return (-1, self.current_term, False)
            
            term = self.current_term
            index = self.get_last_index() + 1
            log_entry = rpc_service_pb2.LogEntry(term=term,
                                                 index=index,
                                                 command=command)
            self.logs.append( log_entry )
            logging.info(f"  RAFT [{self.my_id}] adds entry {term, index} to log")
            return (index, term, True)
    

    """ Call the append_entries RPC of all other RAFT servers
        *** Lock must be acquired before calling this function ***
    """
    def broadcast_append_entries(self):
        logging.info(f"  RAFT [{self.my_id}] - broadcast AE:")
        assert self.lock.locked()
        if self.state != Leader:
            return
        
        for i in range(self.n_replicas):
            if i != self.my_id:
                try:
                    message = f"from {self.my_id} to {i} broadcast"
                    ae_request = rpc_service_pb2.AE_Request()
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
       

    """ Broadcast request_vote RPC to all Raft replicas.
        If receive a majority of vote, will set the event to notify the main loop
        *** Lock must be acquired before calling this function ***
    """
    def broadcast_request_vote(self):
        logging.info(f"  RAFT [{self.my_id, self.state}] - broadcast request vote")
        assert self.lock.locked()
        print(self.current_term)
        if self.current_term == 10:
            print("Receive majority vote !!!! ")
            self.received_majority_vote.set()
    

    """ Convert the current RAFT server to Follower
        - Input: the new term number
        *** Lock must be acquired before calling this function ***
    """
    def convert_to_follower(self, term):
        logging.info(f"  RAFT [{self.my_id, self.state}] - convert to follower - old term: {self.current_term} - new term: {term}")
        assert self.lock.locked
        self.state = Follower
        self.current_term = term
        self.vote_for = None


    """ Convert the current RAFT server to Candidate
    """
    def convert_to_candidate(self):
        logging.info(f"  RAFT [{self.my_id, self.state}] - convert to candidate")
        with self.lock:
            self.state = Candidate
            self.reset_events()
            self.current_term += 1
            self.vote_for = self.my_id
            self.vote_count = 1
            
            self.broadcast_request_vote()
    
    
    """ (Try to) convert the current RAFT server to Leader
    """
    def convert_to_leader(self):
        logging.info(f"  RAFT [{self.my_id, self.state}] - try convert to leader")
        with self.lock:
            # state may change (to Follower) before this function is called, 
            # so need to check the state
            if self.state != Candidate:
                return 
            
            self.state = Leader
            self.reset_events()

            last_log_index = self.get_last_index()
            self.next_index = [last_log_index + 1 for i in range(self.n_replicas)]
            self.match_index = [0 for i in range(self.n_replicas)]

            self.broadcast_append_entries()


    """ Reset events. 
        *** Lock must be acquired before calling this function ***
    """
    def reset_events(self):
        assert self.lock.locked()
        self.heard_heartbeat = False
        self.grant_vote = False
        self.received_majority_vote.clear()


    def main_loop(self):
        while True:
            with self.lock:
                state = self.state
            # print(state)
            
            if state == Leader:
                # sleep(config.leader_broadcast_interval / 1000)
                sleep(1)
                # at this point, the state of the server may already change (to Follower)
                with self.lock:
                    if self.state == Leader:
                        self.broadcast_append_entries()

            elif state == Follower:
                sleep(2)
                with self.lock:
                    to_convert_to_candidate =  (not self.heard_heartbeat) and (not self.grant_vote)
                    self.heard_heartbeat = False
                    self.grant_vote = False
                if to_convert_to_candidate:
                    self.convert_to_candidate()
            
            elif state == Candidate:
                ok =  self.received_majority_vote.wait(2)
                # received majority vote, can convert to leader
                # but state may also have changed (to Follower)
                if ok:
                    self.convert_to_leader()
                elif self.state == Follower:
                    pass
                else:
                    self.convert_to_candidate()


