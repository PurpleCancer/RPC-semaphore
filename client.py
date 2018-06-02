import sys
import asyncio
from rpcudp.protocol import RPCProtocol

@asyncio.coroutine
def lock(protocol, address, locks):
    result = yield from protocol.lock(address, locks)
    print(result[1] if result[0] else "No response received.")

@asyncio.coroutine
def release(protocol, address, locks):
    result = yield from protocol.release(address, locks)
    print(result[1] if result[0] else "No response received.")
    
class RPCServer(RPCProtocol):
    def rpc_go(self, sender):
        print('go')
        return "ok"

if len(sys.argv) < 4:
    print("Usage: server.py server_name server_port client_port")
else:
    loop = asyncio.get_event_loop()
    server_name = sys.argv[1]
    server_port = int(sys.argv[2])
    client_port = int(sys.argv[3])
    
    # Start local UDP server to be able to handle responses
    listen = loop.create_datagram_endpoint(RPCServer, local_addr=('127.0.0.1', client_port))
    transport, protocol = loop.run_until_complete(listen)

    _lock = lock(protocol, (server_name, server_port), 3)
    _release = release(protocol, (server_name, server_port), 7)
    try:
        loop.run_until_complete(_release)
        loop.run_until_complete(_lock)
    finally:
        loop.run_forever()