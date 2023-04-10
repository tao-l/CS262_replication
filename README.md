# CS262_replication


## Design Document
Our approach to replicated chat server is the __replicated state machine__ approach.
Each server maintains a state machine and a log of commands/requests.
Servers takes commands from the client, add the commands to the log, apply the commands to the state machine, and then send responses back to the client. 
The servers use a concensus algorithm to agree on a same sequence of commands.  In particular, we use the [RAFT algoirhtm](https://raft.github.io/raft.pdf).
