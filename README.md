# CS262_replication


## Design Document
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

* When a leader is disconnected with other servers, it may add several commands to its log and cannot commit to them.  Then, a new leader may be elected among other servers.  Then, the previous leader has to become a follower and removes the commited commands in its log.

* ...

We mention these details only to illustrate the difficulty of the problem.  One should read the original paper (or other resources) for the full details of the algorithm. 


### Code structure
