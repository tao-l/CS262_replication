# CS262_replication


## Design Document
Our approach to replicated chat server is the __replicated state machine__ approach.
Each server maintains a state machine and a log of commands/requests.
Servers take commands/requests from the client, add the commands to the log, apply the commands to the state machine, and then send responses back to the client. 
The servers use a concensus algorithm to agree on a same sequence of commands.  In particular, we use the [RAFT algoirhtm](https://raft.github.io/raft.pdf).
This is a leader-follower (or primary-backup) type algorithm: at any time, there is at most one server who is the leader in the system; other servers are followers.
Only the leader can take requests from the client.  After taking a request, the leader broadcasts this request to other servers to ask them to add this request to their logs.  When the leader learns that the request has been replicated on a majority of servers (namely, _committed_), it executes the request (apply the command to the state machhine) and replies to the client.  Followers also execute the committed requests in the logs to update the state machine, without replying to the client.
