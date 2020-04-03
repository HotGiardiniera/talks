import json
import sys
import socketserver
import urllib
from http.server import SimpleHTTPRequestHandler

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


def grpc_serve():
    print("Starting grpc server port 50051...")
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


class Handler(SimpleHTTPRequestHandler):


    def _decode_protobuf(self, body):
        protobuf_message = urllib.parse.unquote(body.decode().split('=')[1]).encode()  # Ugly TODO comments and break down
        proto_obj = SimpleMessage()
        proto_obj.ParseFromString(protobuf_message)
        print("GOT A PROTOBUF MESSAGE!", proto_obj.id, proto_obj.names)

    def _handle_json(self, body):
        decoded_body = json.loads(body.decode())
        print("GOT A JSON MESSAGE!", decoded_body)


    def do_POST(self):
        # Construct a server response.
        content_length = int(self.headers['Content-Length'])
        post_body = self.rfile.read(content_length)
        if self.headers.get('Content-Type', '') == 'protobuf':
            self._decode_protobuf(post_body)
        else:
            self._handle_json(post_body)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # Send the html message
        return_string = f'Recieved {post_body}\nSize{content_length}\n'
        self.wfile.write(return_string.encode())


def http_serve():
    print("Starting http server port 8888...")
    httpd = socketserver.TCPServer(('', 8888), Handler)
    httpd.serve_forever()


if __name__ == "__main__":
    argv = sys.argv[1:]
    SERVER_MAP = {
        'http': http_serve,
        'grpc': grpc_serve,
    }

    if len(argv) < 1:
        print("Need to specify server as program input (http, grpc)")
        exit(-1)

    server = SERVER_MAP.get(argv[0], grpc_serve)()
