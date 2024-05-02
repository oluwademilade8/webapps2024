from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
from timestamp_service.timestamp_service.TimestampService import Client

def get_current_timestamp():
    transport = TSocket.TSocket('localhost', 10000)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = Client(protocol)

    try:
        transport.open()
        timestamp = client.getCurrentTimestamp()
        return timestamp
    finally:
        transport.close()
