import asyncio
import json
import logging
import random
import time

import websockets

import logging
logger = logging.getLogger('websockets.server')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

def serve(loop, video_buffer, server_address=('0.0.0.0', 8766)):

    connections = {}

    @asyncio.coroutine
    def producer():
        # yield from video_buffer.tostring()
        yield from asyncio.sleep(.02)

    @asyncio.coroutine
    def firehose(websocket, path, timeout=1):
        connections[websocket] = True
        while True:
            data = video_buffer.tobytes()
            msg = yield from websocket.send(data)
            x = yield from producer()
            if not websocket.open:
                print("BREAK")
                del connections[websocket]
                break

    logging.info("websockets serving on {}".format(server_address))
    firehose_server = websockets.serve(firehose, *server_address)
    loop.run_until_complete(firehose_server)
