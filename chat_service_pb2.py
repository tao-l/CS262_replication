# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chat_service.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12\x63hat_service.proto\x12\x0c\x63hat_service\"p\n\x07Request\x12\n\n\x02op\x18\x01 \x01(\x05\x12\x0f\n\x07param_1\x18\x02 \x01(\x05\x12\x10\n\x08username\x18\x03 \x01(\t\x12\x13\n\x0btarget_name\x18\x04 \x01(\t\x12\x0f\n\x07message\x18\x05 \x01(\t\x12\x10\n\x08wildcard\x18\x06 \x01(\t\"I\n\x08Response\x12\n\n\x02op\x18\x01 \x01(\x05\x12\x0e\n\x06status\x18\x02 \x01(\x05\x12\x10\n\x08username\x18\x03 \x01(\t\x12\x0f\n\x07message\x18\x04 \x01(\t2O\n\x0b\x43hatService\x12@\n\x0brpc_request\x12\x15.chat_service.Request\x1a\x16.chat_service.Response\"\x00\x30\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chat_service_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _REQUEST._serialized_start=36
  _REQUEST._serialized_end=148
  _RESPONSE._serialized_start=150
  _RESPONSE._serialized_end=223
  _CHATSERVICE._serialized_start=225
  _CHATSERVICE._serialized_end=304
# @@protoc_insertion_point(module_scope)