#!/usr/bin/env python

import asyncio
import websockets

@asyncio.coroutine
def hello():
    websocket = yield from websockets.connect('ws://localhost:8765/')
    while True:
        msg = yield from websocket.recv()
        print( msg)

asyncio.get_event_loop().run_until_complete(hello())
