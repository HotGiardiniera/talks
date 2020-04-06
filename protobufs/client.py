#!/usr/bin/env python

import grpc
import requests

from pb import messages_pb2_grpc
from pb.messages_pb2 import MessageRequest, SimpleMessage

SERVER = 'http://192.168.1.100:8888'

def run_grpc():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = messages_pb2_grpc.SimpleServiceStub(channel)
        message = MessageRequest(
            message=SimpleMessage(
                id=1,
                names=['one', 'two', 'three'],
                nums=[1,2,3],
                is_json=False
            )
        )
        print("Trying to send message")
        response = stub.HandleMessage(message)
    print("Response recieved received: " + response.type)

def send_http_json():
    json_payload = {'id': 200, 'array': [1, 2, 3, 400], 'other_obj': {'id': 2}}
    requests.post(SERVER, json=json_payload)


def send_http_protobuf():
    s = SimpleMessage(id=200, array=[1,2,3,400], other_obj=SimpleMessage.OtherObj(id=2))
    headers={'content-type': 'application/octet-stream'}
    requests.post(SERVER, data={'data': s.SerializeToString()}, headers=headers)


if __name__ == "__main__":
    send_http_json()
    # send_http_protobuf()
