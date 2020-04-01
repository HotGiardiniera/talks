import grpc

from pb import messages_pb2_grpc
from pb.messages_pb2 import MessageRequest, SimpleMessage


def run():
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


if __name__ == "__main__":
    run()
