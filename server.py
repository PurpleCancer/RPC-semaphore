import sys
import asyncio
import functools
from rpcudp.protocol import RPCProtocol
from queue import Queue

loop = asyncio.get_event_loop()
protocol = 0

@asyncio.coroutine
def reply(client):
        result = yield from protocol.go(client)
        print(result[1] if result[0] else "No response received.")

@asyncio.coroutine
def lock_and_reply(client, locks):
    yield from RPCServer.lock
    try:
        if RPCServer.queue.empty():
            if locks <= RPCServer.locks:
                print("%d locks taken by %s" % (locks, str(client[0])))
                asyncio.ensure_future(reply(client))
            else:
                print("%s added to queue" % str(client[0]))
                RPCServer.queue.put((client, locks))
        else:
            print("%s added to queue" % str(client[0]))
            RPCServer.queue.put((client, locks))
    finally:
        RPCServer.lock.release()

@asyncio.coroutine
def release(client, locks):
    yield from RPCServer.lock
    try:
        RPCServer.locks += locks
        print("%d locks released by %s" % (locks, str(client[0])))
    finally:
        RPCServer.lock.release()

class RPCServer(RPCProtocol):
    lock = asyncio.Lock()
    locks = 0
    queue = Queue()
    
    def rpc_lock(self, sender, locks):
        _lock = lock_and_reply(sender, locks)
        asyncio.ensure_future(_lock)
        return "ok"
    def rpc_release(self, sender, locks):
        _release = release(sender, locks)
        asyncio.ensure_future(_release)
        return "ok"

if len(sys.argv) < 2:
    print("Usage: server.py port")
else:
    port = int(sys.argv[1])
    listen = loop.create_datagram_endpoint(RPCServer, local_addr=('127.0.0.1', port))
    transport, protocol = loop.run_until_complete(listen)
    loop.run_forever()