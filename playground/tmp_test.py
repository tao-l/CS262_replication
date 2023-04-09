import raft


import config



class ChatServiceServicer(rpc_service_pb2_grpc.ChatServiceServicer):

    """ Customized initialization """
    def my_init(self, replicas, my_id):
        # create a RAFT server and start it
        self.rf = raft.RaftServiceServicer(replicas, id, self.apply_queue)
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=128))
        rpc_service_pb2_grpc.add_RaftServiceServicer_to_server(self.rf, server)
        my_ip_addr = replicas[my_id].ip_addr
        raft_port = replicas[my_id].raft_port
        server.add_insecure_port(my_ip_addr + ":" + raft_port)
        print(f"  RAFT server {my_id} starts at {my_ip_addr}:{raft_port}")
        server.start()
        threading.Thread(target=server.wait_for_termination, args=()).start()
    

def TEST_rpc_append_entries():
    rf = raft.RaftServiceServicer()



        
        
        
