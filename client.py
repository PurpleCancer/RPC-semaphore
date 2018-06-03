import sys
import asyncio
from rpcudp.protocol import RPCProtocol

loop = asyncio.get_event_loop()

@asyncio.coroutine
def lock(protocol, address, locks):
    success = False
    while not success:
        result = yield from protocol.lock(address, locks)
        success = result[0]
        if not result[0]:
            print("No response received, retrying")

@asyncio.coroutine
def release(protocol, address, locks):
    success = False
    while not success:
        result = yield from protocol.release(address, locks)
        success = result[0]
        if not result[0]:
            print("No response received, retrying")

class RPCServer(RPCProtocol):
    def rpc_go(self, sender):
        loop.stop()
        return "ok"

def lock_wrapper(locks):
    _lock = lock(protocol, (server_name, server_port), locks)
    try:
        loop.run_until_complete(_lock)
    finally:
        loop.run_forever()

def release_wrapper(locks):
    _release = release(protocol, (server_name, server_port), locks)
    try:
        loop.run_until_complete(_release)
    finally:
        loop.stop()

if len(sys.argv) < 4:
    print("Usage: server.py server_name server_port client_port")
else:
    server_name = sys.argv[1]
    server_port = int(sys.argv[2])
    client_port = int(sys.argv[3])
    
    # Start local UDP server to be able to handle responses
    listen = loop.create_datagram_endpoint(RPCServer, local_addr=('127.0.0.1', client_port))
    transport, protocol = loop.run_until_complete(listen)

    operation = input("What operation to perform? (lock/release)\n")
    if operation == "lock" or operation == "release":
        locks = int(input("How many locks?\n"))
        if operation == "lock":
            lock_wrapper(locks)
        elif operation == "release":
            release_wrapper(locks)
        print("Complete.")
    else:
        print("Bad operation.")

