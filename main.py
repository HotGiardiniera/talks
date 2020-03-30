from pb.messages_pb2 import Message


def write_to_file_proto(obj: Message, filename: str = 'pb_out'):
    with open(filename, 'wb') as file:
        file.write(obj.SerializeToString())


def read_message_from_file(filename: str):
    proto_obj = Message()
    with open(filename, 'rb') as file:
        proto_obj.ParseFromString(file.read())
    return proto_obj
