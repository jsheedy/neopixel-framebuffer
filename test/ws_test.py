#!/usr/bin/env python

import asyncio
import websockets

@asyncio.coroutine
def hello(websocket, path):
    name = yield from websocket.recv()
    print("< {}".format(name))
    greeting = "XHello {}!".format(name)
    yield from websocket.send(greeting)
    print("> {}".format(greeting))

start_server = websockets.serve(hello, 'localhost', 8765)
asyncio.get_event_loop().run_until_complete(start_server)

import time
import random
def producer():
    while True:
        time.sleep(.005)
        yield str(random.random())

@asyncio.coroutine
def firehose(websocket, path):
    while True:
        message = next(producer())
        # message = "foo"
        # message = yield from producer()
        if not websocket.open:
            break
        yield from websocket.send(message)
        print(message)

firehose_server = websockets.serve(firehose, 'localhost', 8766)
asyncio.get_event_loop().run_until_complete(firehose_server)
asyncio.get_event_loop().run_forever()
