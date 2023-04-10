F = 2      # number of faulty recplicas we want to tolerate

need_persistent = False      # whether we need our servers to be persistent

local = True        # whether to run the system locally

class ServerInfo():
    def __init__(self, id, ip_addr, client_port, raft_port):
        self.id = id, 
        self.ip_addr = ip_addr
        self.client_port = client_port
        self.raft_port = raft_port
        self.host_addr = None

replicas = ( ServerInfo(0, "10.250.199.106", "20000", "30000"), 
             ServerInfo(1, "10.250.199.106", "20010", "30010"), 
             ServerInfo(2, "10.250.82.111", "20020", "30020"), 
             # ServerInfo(3, "127.0.0.1", "20030", "30030"), 
             # ServerInfo(4, "127.0.0.1", "20040", "30040")
           )

if local:
    for x in replicas:
        x.ip_addr = "127.0.0.1"

n_replicas = len(replicas)
# assert n_replicas > 2*F


leader_broadcast_interval = 40  # millisecond
election_timeout_lower_bound = 200
election_timeout_upper_bound = 400





CREATE_ACCOUNT = 1
CHECK_ACCOUNT = 2
LIST_ACCOUNT = 3
DELETE_ACCOUNT = 4
SEND_MESSAGE = 5
FETCH_MESSAGE = 6


USERNAME_LIMIT = 20
MESSAGE_LIMIT = 500


SUCCESS = 0

NO_ELEMENT = 1

 # error codes: range in [100, 199]
OPERATION_NOT_SUPPORTED = 100
INVALID_USERNAME = 101
ACCOUNT_NOT_EXIST = 102
MESSAGE_TOO_LONG = 103
MESSAGE_ID_TOO_LARGE = 104
GENERAL_ERROR = 199


SERVER_ERROR = 190