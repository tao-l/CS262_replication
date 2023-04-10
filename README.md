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

The number of servers and their addresses and ports are in `config.py`.  To change the number of servers, just change the `replicas` list. 

To run the servers locally, change the ip addresses to `127.0.0.1` or just set `local = True' in `config.py`. 

__Persistence:__ The servers can be run in two modes: persistent or not.  To specify this, change the `need_persistent` in `config.py` to True or False.
In the persistent mode, servers will save states to files `record0', `recor1', etc. 

__To run a client__, run:

```console
$ python3 client.py
```

# Design Document

Our approach to replicated chat server is the __replicated state machine__ approach.
Each server maintains a state machine and a log of commands/requests.
Servers take commands/requests from the client, add the commands to the log, apply the commands to the state machine, and then send responses back to the client. 
The servers use a consensus algorithm to agree on the same sequence of commands.
In particular, we implement the [RAFT algoirhtm](https://raft.github.io/raft.pdf), which was proposed as "an alternative to PAXOS".  This algorithm can tolerate server crashes, network faults and delays, different processing speeds of different servers, etc. 

RAFT is a leader-follower algorithm.  The full algorithm is complicated.  We only give a high-level overview here.  Roughly speaking, the algorithm works as follows: 

1. It works term by term.  At the beginning of each term, a server is elected as a Leader.  Other servers are Followers.

2. Only the Leader can take requests from the client.  After taking a request, the Leader adds the request to its own log.  This request is not committed and cannot be executed immediately.

3. The Leader periodically broadcasts its log to the Followers, asking them to replicate this log.

4. When the Leader learns that a request on the log has been replicated on a majority of all servers, this request is considered committed and the Leader executes this request (namely, applies this command to the state machine) and responds to the client.

5. Followers listen to the Leader's broadcasts, and append new entries to their own logs if the Leader's log has new entries.  If the Leader's log is different from their logs, they replace their logs with the Leader's.  The Leader also tells the Followers which log entries have been committed, and the Followers can execute those entries.

6. If a Follower cannot hear the Leader for some period, the Leader is considered faulty and the Follower starts a new term and runs an election in order to be the new Leader.  To do this, this candidate server requests votes from every other server.  If it receives a majority of votes, then it becomes the Leader.  When deciding whether to vote for a candidate, a server has to compare its own log with the candidate's log and grants vote only if the candidate's log is newer than its log.  This ensures that the Leader always has the "latest" log.  If no Leader can be elected due to split votes, a Follower starts a new election again after some random timeout.  Eventually, some new Leader will be elected.  

We omit many details here.  One can read the [original paper](https://raft.github.io/raft.pdf) or other resources for details.

## Failure Modes We Support
Because we implemented the RAFT algorithm, our server can survive all the failures that RAFT can survice, including: 

1. At most 2 out of 5 servers crush.  
2. At most 2 out of 5 servers cannot connect to other servers due to network failures.
3. Crushed server can be restarted.  Even after 3 or more servers crush, as long as some servers are restarted so that 3 servers are running, our system can return to work. 

## Design Decisions and Code Structure

### Server

Each of our server (a `ChatServiceServicer` object in `server.py`) contains two components:

* a state machine `state_machine` (which is a `ChatStateMachine` object defined in `server_state_machine.py`), and
* a RAFT instance `rf` (which is a `RaftServiceServicer` object defined in `raft.py`).

The server offers RPC services to the client.  When receiving an RPC request from the client, the server asks the RAFT instance (by calling `rf.new_entry(request)`) to add this request to its log.  The RAFT instance will communicate with the RAFT instances on other servers to replicate this request.  The replication is not guaranteed to succeed (e.g., because the current server is not the leader).  When the request is replicated on a majority of servers, this request is considered committed, and the RAFT instance will notify the server to apply this request (by putting the request into the server's `apply_queue`).   Then, the server applies this request to the state machine (calling `state_machine.apply(request)` function) and replies to the client.  If this request is replicated from other servers, do not reply to the client.  The servers never directly communicate with each other -- they communicate via the RAFT instances only. 

The state machine `state_machine` implements the main logic of the chat server.  A request can be one of the 6 operations: `{create_account, check_account, list_account, delete_account, send_message, fetch_messages}`, indicated by `request.op`.  Other parameters of the request are stored in, e.g., `request.username` and `request.message` (see `rpc_service.proto` for details).  The `state_machine.apply(request)` function executes this request and returns the response.  The server will then forward this response to the client if needed.

#### Why this design?

Our design completely separates the logic of the consensus/replication algorithm (RAFT) and the logic of the state machine (the specific chat services).
RAFT does not know anything about the state machine and the state machine does not need to worry about replication.  This makes the design more modular and makes all the RAFT code, the state machine code, and the server code re-usable in other problems.  For example, if we want to implement a replicated system for another service, we only need to replace the state machine code without changing the server code and RAFT code. 

### Client

The client does not know which server is the leader, so it just calls all servers one by one until receiving a valid reply (a non-leader server replies with an error message).
Occasionally, all the servers will be unavailable due to, e.g., leader election, in which the client has to deal with errors.  Other details are not very important. 
