import threading
from datetime import datetime
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport

# Import the generated classes
from timestamp_service.TimestampService import Iface
from timestamp_service.TimestampService import Processor

class TimestampServiceHandler(Iface):
    def getCurrentTimestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def start_server():
    handler = TimestampServiceHandler()
    processor = Processor(handler)
    transport = TSocket.TServerSocket(host='127.0.0.1', port=10000)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    print("Starting the server...")
    server.serve()
    print("Done.")

def run_server():
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

if __name__ == "__main__":
    run_server()
