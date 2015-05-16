import asyncio
import json
import logging
import random
import time

import websockets

def serve(loop, video_buffer, server_address=('0.0.0.0', 8766)):

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

    logging.info("websockets serving on {}".format(server_address))
    firehose_server = websockets.serve(firehose, *server_address)
    loop.run_until_complete(firehose_server)
