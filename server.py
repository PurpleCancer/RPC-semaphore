import sys
import asyncio
import functools
from rpcudp.protocol import RPCProtocol
from collections import deque

loop = asyncio.get_event_loop()
protocol = 0

@asyncio.coroutine
def reply(client):
    result = yield from protocol.go(client)
    if not result[0]:
        print("No response received")

@asyncio.coroutine
def check_and_reply():
    yield from RPCServer.lock
    try:
        if len(RPCServer.queue) > 0:
            while len(RPCServer.queue) > 0 and RPCServer.queue[0][1] <= RPCServer.locks:
                front = RPCServer.queue.popleft()
                RPCServer.locks -= front[1]
                asyncio.ensure_future(reply(front[0]))
                print("%d locks taken by %s" % (front[1], str(front[0])))
    finally:
        RPCServer.lock.release()

@asyncio.coroutine
def lock_and_reply(client, locks):
    yield from RPCServer.lock
    try:
        if len(RPCServer.queue) == 0:
            if locks <= RPCServer.locks:
                RPCServer.locks -= locks
                print("%d locks taken by %s" % (locks, str(client[0])))
                asyncio.ensure_future(reply(client))
            else:
                print("%s added to queue" % str(client[0]))
                RPCServer.queue.append((client, locks))
        else:
            print("%s added to queue" % str(client[0]))
            RPCServer.queue.append((client, locks))
    finally:
        RPCServer.lock.release()

@asyncio.coroutine
def release(client, locks):
    yield from RPCServer.lock
    try:
        RPCServer.locks += locks
        print("%d locks released by %s" % (locks, str(client[0])))
        asyncio.ensure_future(check_and_reply())
    finally:
        RPCServer.lock.release()

class RPCServer(RPCProtocol):
    lock = asyncio.Lock()
    locks = 0
    queue = deque()
    
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
