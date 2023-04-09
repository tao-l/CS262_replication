import grpc
import rpc_service_pb2_grpc
import rpc_service_pb2 as pb2


chat_request = pb2.ChatRequest()
chat_request.message = "this is a chat request"

log_entry = pb2.LogEntry(term=1, chat_request=chat_request)

AE_request = pb2.AE_Request()
AE_request.entries.append(log_entry)
AE_request.entries.extend([log_entry, log_entry])

bin = AE_request.SerializeToString()
# AE_request2 = pb2.AE_Request()
# AE_request2.ParseFromString(bin)

AE_request2 = AE_request
AE_request3 = pb2.AE_Request()
AE_request3.CopyFrom(AE_request)

AE_request.entries[0].term = 100

print(AE_request2.entries)
print(AE_request3.entries)