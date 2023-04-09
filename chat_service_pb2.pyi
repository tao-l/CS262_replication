from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Request(_message.Message):
    __slots__ = ["message", "op", "param_1", "target_name", "username", "wildcard"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    OP_FIELD_NUMBER: _ClassVar[int]
    PARAM_1_FIELD_NUMBER: _ClassVar[int]
    TARGET_NAME_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    WILDCARD_FIELD_NUMBER: _ClassVar[int]
    message: str
    op: int
    param_1: int
    target_name: str
    username: str
    wildcard: str
    def __init__(self, op: _Optional[int] = ..., param_1: _Optional[int] = ..., username: _Optional[str] = ..., target_name: _Optional[str] = ..., message: _Optional[str] = ..., wildcard: _Optional[str] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ["message", "op", "status", "username"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    OP_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    message: str
    op: int
    status: int
    username: str
    def __init__(self, op: _Optional[int] = ..., status: _Optional[int] = ..., username: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...
