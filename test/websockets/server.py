#!/usr/bin/env python

import asyncio
import websockets
import time

@asyncio.coroutine
def hello(websocket, path):
    while True:
        msg = str(time.time())
        yield from websocket.send(msg)
        time.sleep(.1)

start_server = websockets.serve(hello, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
