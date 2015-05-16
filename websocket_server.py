import asyncio
import json
import random
import time

import websockets

def serve(loop, video_buffer):

    @asyncio.coroutine
    def producer():
        # yield from video_buffer.tostring()
        yield from asyncio.sleep(.05)

    @asyncio.coroutine
    def firehose(websocket, path, timeout=1):
        while True:
            x = yield from producer()
            data = video_buffer.tostring()
            if not websocket.open:
                print("BREAK")
                break
            msg = yield from websocket.send(data)

    # asyncio.set_event_loop(loop)
    firehose_server = websockets.serve(firehose, '0.0.0.0', 8766)
    # asyncio.get_event_loop().run_until_complete(firehose_server)
    loop.run_until_complete(firehose_server)
    # asyncio.get_event_loop().run_forever()