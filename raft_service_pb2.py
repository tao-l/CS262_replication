# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: raft_service.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12raft_service.proto\x12\x0craft_service\"\x1d\n\nAE_Request\x12\x0f\n\x07message\x18\x01 \x01(\t\"\x1e\n\x0b\x41\x45_Response\x12\x0f\n\x07message\x18\x04 \x01(\t2Z\n\x0bRaftService\x12K\n\x12rpc_append_entries\x12\x18.raft_service.AE_Request\x1a\x19.raft_service.AE_Response\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'raft_service_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _AE_REQUEST._serialized_start=36
  _AE_REQUEST._serialized_end=65
  _AE_RESPONSE._serialized_start=67
  _AE_RESPONSE._serialized_end=97
  _RAFTSERVICE._serialized_start=99
  _RAFTSERVICE._serialized_end=189
# @@protoc_insertion_point(module_scope)