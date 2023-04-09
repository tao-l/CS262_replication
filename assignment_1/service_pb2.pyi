from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ChatMessage(_message.Message):
    __slots__ = ["message", "status", "target_name", "username"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TARGET_NAME_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    message: str
    status: int
    target_name: str
    username: str
    def __init__(self, username: _Optional[str] = ..., target_name: _Optional[str] = ..., message: _Optional[str] = ..., status: _Optional[int] = ...) -> None: ...

class FetchRequest(_message.Message):
    __slots__ = ["msg_id", "username"]
    MSG_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    msg_id: int
    username: str
    def __init__(self, msg_id: _Optional[int] = ..., username: _Optional[str] = ...) -> None: ...

class GeneralResponse(_message.Message):
    __slots__ = ["message", "status"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    message: str
    status: int
    def __init__(self, status: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class User(_message.Message):
    __slots__ = ["username"]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    username: str
    def __init__(self, username: _Optional[str] = ...) -> None: ...

class Wildcard(_message.Message):
    __slots__ = ["wildcard"]
    WILDCARD_FIELD_NUMBER: _ClassVar[int]
    wildcard: str
    def __init__(self, wildcard: _Optional[str] = ...) -> None: ...
