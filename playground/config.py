F = 2

class ServerInfo():
    def __init__(self, id, ip_addr, client_port, raft_port):
        self.id = id, 
        self.ip_addr = ip_addr
        self.client_port = client_port
        self.raft_port = raft_port

replicas = ( ServerInfo(0, "127.0.0.1", "20000", "30000"), 
             ServerInfo(1, "127.0.0.1", "20010", "30010"), 
             ServerInfo(2, "127.0.0.1", "20020", "30020"), 
             ServerInfo(3, "127.0.0.1", "20030", "30030"), 
             ServerInfo(4, "127.0.0.1", "20040", "30040")
           )

n_replicas = len(replicas)
assert n_replicas > 2*F

leader_broadcast_interval = 100  # millisecond
