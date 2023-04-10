# CS262_replication

# Running the Programs
Make sure you have installed the gRPC python package first.  If you haven't, run:
```console
$ python3 -m pip install --upgrade pip
$ python3 -m pip install grpcio
$ python3 -m pip install grpcio-tools
```
(If you encounter problems when installing gRPC, check [their website](https://grpc.io/docs/languages/python/quickstart/).)

First, download or clone our github repository.  To clone, cd into a folder where you want to put this repository and run: 
```console
$ git clone https://github.com/tao-l/CS262_replication.git
```
Then, cd into the repository: 
```console
$ cd CS262_replication
```

__To run the servers__, open multiple terminals (and cd into the above directory), in each terminal, run: 
```console
$ python3 server.py id
```
where `id` is a number in `[0, 1, 2, 3, 4]` indicating the id of the server.  (To tolerate 2 faults, we need 5 servers).  You will see something like the following:
```console
  Retrieved!  current_term = 131, voted_for = 0, log_len = 72
  RAFT [1] RPC server starts at 127.0.0.1:30010
  RAFT [1] main loop starts.
 ====== Chat server [1] starts at 127.0.0.1:20010 =======
INFO:root:  RAFT [1] - convert to Candidate from state 0
INFO:root:    RAFT [1], state = [0], last_applied=[0], commit_index=[0], log length = [71], term=[131]
INFO:root:    RAFT [1], state = [0], last_applied=[0], commit_index=[0], log length = [71], term=[138]
```
where [1] is the id of the server. 

The number of servers and their addresses and ports are in `config.py`.  To run the servers locally, change the ip address to `127.0.0.1`.  To change the number of servers, just change the `replicas` list. 


__To run a client__, run:
```console
$ python3 server.py id
```


# Design Document
Our approach to replicated chat server is the __replicated state machine__ approach.
Each server maintains a state machine and a log of commands/requests.
Servers take commands/requests from the client, add the commands to the log, apply the commands to the state machine, and then send responses back to the client. 
The servers use a concensus algorithm to agree on a same sequence of commands.
In particular, we implement the [RAFT algoirhtm](https://raft.github.io/raft.pdf), which was proposed as "an alternative to PAXOS".
This algorithm can tolerate server crashes/failstops, network faults and delays, different processing speeds of different servers, etc.

RAFT is a leader-follower type algorithm.  At any time, there is at most one server who is the leader in the system; other servers are followers.
Only the leader can take requests from the client.  After taking a request, the leader broadcasts this request to other servers to ask them to add this request to their logs.  When the leader learns that the request has been replicated on a majority of servers (namely, _committed_), it executes the request (namely, applies the command to the state machhine) and replies to the client.  Followers also execute the committed requests in the logs to update the state machine, without replying to the client.
This is only a high-level description, however.  There are many details in the RAFT algorithm to ensure that all servers have the same log of commited requests.  For example, 

* When the leader crashes and a new leader needs to be elected, some servers cannot be elected because they may have not received all the commited requests due to network delay.  We must choose a server with the "latest" log. 

* When a leader is disconnected with other servers, it may add several commands to its log and cannot commit to them.  Then, a new leader may be elected among other servers.  Then, the previous leader has to become a follower and removes the committed commands in its log.

* ...

We mention the above examples only to illustrate the difficulties of the problem and importance of details.  One should read the [original paper](https://raft.github.io/raft.pdf) (or other resources) for the full description of the RAFT algorithm. 


## Design Decision and Code Structure
### Server
Each of our server (an `ChatServiceServicer` object in `server.py`) contains two components:

* a state machine `state_machine` (which is a `ChatStateMachine` object defined in `state_machine.py`), and
* a RAFT instance `rf` (which is a `RaftServiceServicer` object defined in `raft.py`).

The server offers RPC services to the client.  When receiving a RPC request from the client, the server asks the RAFT instance (by calling `rf.new_entry(request)`) to add this request to its log.  The RAFT instance will communicate with the RAFT instances on other servers to replicate this request.  The replication is not guaranteed to succeed (e.g., because the current server is not the leader).  When the request has been replicated on a majority of servers, this request is considered committed, and the RAFT instance will notify the server to apply this request (by putting the request to the server's `apply_queue`).   Then server then applies this request by calling the state machine (calling `state_machine.apply(request)` function), and replies to the client (if this request is replicated from other servers, do not reply to client).  The servers never directly communicate with each other -- they communicate over the RAFT instances. 

The state machine `state_machine` implements the main logic of the chat server.  A request can be one of the 6 operations: `{create_account, check_account, list_account, delete_account, send_message, fetch_messages}`, indicated by `request.op`.  Other parameters of the request are stored in, e.g., `request.username` and `request.message` (see `rpc_service.proto` for details).  The `state_machine.apply(request)` function executes this request and returns the response.  The server will then forward this response to the client.

#### Why this design? 
Our design completely separates the logic of the concensus/replication algorithm (RAFT) and the logic of the state machine (the specific chat services).
RAFT does not know anything about how the state machine is implemented and the state machine does not need to worry about replication. 
This makes the design more modular and makes all the RAFT code, the state machine code, and the server code useable in other problems.
For example, if we want to implement a replicated system for another service, we only need to replace the state machine code without changing server code and RAFT code. 

### Client
The client does not know which server is the leader, so it just calls each server one by one until receiving a valid reply (a non-leader server relies an error message).
Occasionally, the service will be unavailable due to, e.g., leader election.  If the client waits for a reply for a long time, it stops and prints an error message.  Other details are not very important. 

