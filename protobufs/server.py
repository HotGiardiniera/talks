#!/usr/bin/env python

import binascii
import json
import sys
import socketserver
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
        response = MessageResponse()
        response.id = self._increment_id()
        print("PROTOBUF MESSAGE VALUES\n", request)
        return response


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
        # Since the POST is encoded to ascii we run into issues with  ecoding. This hack converts the text sent
        # via http and converts the textual representation into bytes

        message_as_text = body.decode().split('=')[1].replace('%', ' ').split(' ')
        print(f'Message bytes as text {message_as_text}')
        byte_list = [binascii.a2b_hex(x) for x in message_as_text if x]
        byte_arr = bytearray()
        for b in byte_list:
            byte_arr.append(b[0])
        proto_obj = SimpleMessage()
        proto_obj.ParseFromString(byte_arr)
        print(f'Original body: {body}')
        print(f'Actual bytes: {byte_arr}')
        print("PROTOBUF MESSAGE VALUES", proto_obj.id, proto_obj.array, proto_obj.other_obj)

    def _handle_json(self, body):
        decoded_body = json.loads(body.decode())
        print("JSON MESSAGE VALUES", json.dumps(decoded_body, indent=4))


    def do_POST(self):
        # Construct a server response.
        content_length = int(self.headers['Content-Length'])
        post_body = self.rfile.read(content_length)
        if self.headers.get('Content-Type', '') == 'application/octet-stream':
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
