import logging
import raft_service_pb2
import raft_service_pb2_grpc

import threading
import random

from time import sleep

class LogEntry:
    def __init__(self, term=-1, index=-1, command=None):
        self.term = term
        self.index = index
        self.command = command


class RaftServiceServicer(raft_service_pb2_grpc.RaftServiceServicer):

    def __init__(self, apply_queue):

        self.apply_queue = apply_queue
        self.lock = threading.Lock()

        self.current_term = -1 
        self.logs = []

        super().__init__()


    def rpc_append_entries(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')
    

    def start(self, command):
        logging.info("  Raft - start: " + command.message)
        
        self.lock.acquire()
        term = self.current_term
        index = len(self.logs)
        self.logs.append( LogEntry(term, index, command) )
        logging.info(f"  Raft: append entry {term, index} to log")
        self.lock.release()

        is_leader = True
        
        def put_command_later(t):
            sleep(t)
            self.lock.acquire()
            self.apply_queue.put(self.logs[index])
            self.lock.release()
        
        threading.Thread(target=put_command_later, args=(random.random(),)).start()

        return (index, term, is_leader)
    

