# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import service_pb2 as service__pb2


class ChatRoomStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.rpc_create_account = channel.unary_unary(
                '/chatroom.ChatRoom/rpc_create_account',
                request_serializer=service__pb2.User.SerializeToString,
                response_deserializer=service__pb2.GeneralResponse.FromString,
                )
        self.rpc_check_account = channel.unary_unary(
                '/chatroom.ChatRoom/rpc_check_account',
                request_serializer=service__pb2.User.SerializeToString,
                response_deserializer=service__pb2.GeneralResponse.FromString,
                )
        self.rpc_list_account = channel.unary_stream(
                '/chatroom.ChatRoom/rpc_list_account',
                request_serializer=service__pb2.Wildcard.SerializeToString,
                response_deserializer=service__pb2.User.FromString,
                )
        self.rpc_delete_account = channel.unary_unary(
                '/chatroom.ChatRoom/rpc_delete_account',
                request_serializer=service__pb2.User.SerializeToString,
                response_deserializer=service__pb2.GeneralResponse.FromString,
                )
        self.rpc_send_message = channel.unary_unary(
                '/chatroom.ChatRoom/rpc_send_message',
                request_serializer=service__pb2.ChatMessage.SerializeToString,
                response_deserializer=service__pb2.GeneralResponse.FromString,
                )
        self.rpc_fetch_message = channel.unary_stream(
                '/chatroom.ChatRoom/rpc_fetch_message',
                request_serializer=service__pb2.FetchRequest.SerializeToString,
                response_deserializer=service__pb2.ChatMessage.FromString,
                )


class ChatRoomServicer(object):
    """Missing associated documentation comment in .proto file."""

    def rpc_create_account(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def rpc_check_account(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def rpc_list_account(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def rpc_delete_account(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def rpc_send_message(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def rpc_fetch_message(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ChatRoomServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'rpc_create_account': grpc.unary_unary_rpc_method_handler(
                    servicer.rpc_create_account,
                    request_deserializer=service__pb2.User.FromString,
                    response_serializer=service__pb2.GeneralResponse.SerializeToString,
            ),
            'rpc_check_account': grpc.unary_unary_rpc_method_handler(
                    servicer.rpc_check_account,
                    request_deserializer=service__pb2.User.FromString,
                    response_serializer=service__pb2.GeneralResponse.SerializeToString,
            ),
            'rpc_list_account': grpc.unary_stream_rpc_method_handler(
                    servicer.rpc_list_account,
                    request_deserializer=service__pb2.Wildcard.FromString,
                    response_serializer=service__pb2.User.SerializeToString,
            ),
            'rpc_delete_account': grpc.unary_unary_rpc_method_handler(
                    servicer.rpc_delete_account,
                    request_deserializer=service__pb2.User.FromString,
                    response_serializer=service__pb2.GeneralResponse.SerializeToString,
            ),
            'rpc_send_message': grpc.unary_unary_rpc_method_handler(
                    servicer.rpc_send_message,
                    request_deserializer=service__pb2.ChatMessage.FromString,
                    response_serializer=service__pb2.GeneralResponse.SerializeToString,
            ),
            'rpc_fetch_message': grpc.unary_stream_rpc_method_handler(
                    servicer.rpc_fetch_message,
                    request_deserializer=service__pb2.FetchRequest.FromString,
                    response_serializer=service__pb2.ChatMessage.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'chatroom.ChatRoom', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ChatRoom(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def rpc_create_account(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chatroom.ChatRoom/rpc_create_account',
            service__pb2.User.SerializeToString,
            service__pb2.GeneralResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def rpc_check_account(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chatroom.ChatRoom/rpc_check_account',
            service__pb2.User.SerializeToString,
            service__pb2.GeneralResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def rpc_list_account(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/chatroom.ChatRoom/rpc_list_account',
            service__pb2.Wildcard.SerializeToString,
            service__pb2.User.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def rpc_delete_account(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chatroom.ChatRoom/rpc_delete_account',
            service__pb2.User.SerializeToString,
            service__pb2.GeneralResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def rpc_send_message(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chatroom.ChatRoom/rpc_send_message',
            service__pb2.ChatMessage.SerializeToString,
            service__pb2.GeneralResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def rpc_fetch_message(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/chatroom.ChatRoom/rpc_fetch_message',
            service__pb2.FetchRequest.SerializeToString,
            service__pb2.ChatMessage.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
