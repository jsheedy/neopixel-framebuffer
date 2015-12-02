import asyncio
import json
import logging
import random
import time

import websockets

import logging
logger = logging.getLogger('websockets.server')
logger.setLevel(logging.INFO)
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
        frame = 0
        while True:
            if video_buffer.frame > frame:
                logging.debug('websocket {} reserving frame {}'.format(websocket, video_buffer.frame))
                frame = video_buffer.frame
            else:
                frame = video_buffer.update()

            data = video_buffer.buffer.tobytes()
            msg = yield from websocket.send(data)
            x = yield from producer()
            if not websocket.open:
                print("BREAK")
                del connections[websocket]
                break

    logging.info("websockets serving on {}".format(server_address))
    firehose_server = websockets.serve(firehose, *server_address)
    loop.run_until_complete(firehose_server)
