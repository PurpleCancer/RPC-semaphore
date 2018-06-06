# RPC-semaphore
Sempahore using RPC in Python.
Library used: [RPCUDP](https://github.com/bmuller/rpcudp)

# Usage
### Running server:
```
pyhton3 server.py SERVER_PORT
```
### Running client:
```
pyhton3 client.py SERVER_ADDRESS SERVER_PORT CLIENT_PORT
```
Client script asks for an action (lock/release) to perform and how many locks to use, but included functions could be easily used in code needing semaphore synchronization.
