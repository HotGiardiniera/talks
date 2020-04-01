import grpc
from grpc_reflection.v1alpha import reflection

from concurrent import futures

from pb import messages_pb2
from pb import messages_pb2_grpc
from pb.messages_pb2 import SimpleMessage, MessageResponse


class SimpleServiceServicer(messages_pb2_grpc.SimpleServiceServicer):

    _INTERNAL_ID = 0

    @classmethod
    def _increment_id(cls) -> int:
        ret = cls._INTERNAL_ID
        cls._INTERNAL_ID += 1
        return ret

    def HandleMessage(self, request, context):
        print("Got message response")
        response = MessageResponse()
        response.id = self._increment_id()
        response.type = "json" if request.message.is_json else "protobuf"
        return response


def write_to_file_proto(obj: SimpleMessage, filename: str = 'pb_out'):
    with open(filename, 'wb') as file:
        file.write(obj.SerializeToString())


def read_message_from_file(filename: str):
    proto_obj = SimpleMessage()
    with open(filename, 'rb') as file:
        proto_obj.ParseFromString(file.read())
    return proto_obj


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    messages_pb2_grpc.add_SimpleServiceServicer_to_server(SimpleServiceServicer(), server)
    SERVICE_NAMES = (
        messages_pb2.DESCRIPTOR.services_by_name['SimpleService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    print("Starting the grpc server...")
    serve()
