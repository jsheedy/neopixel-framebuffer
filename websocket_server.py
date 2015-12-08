import asyncio
from datetime import datetime
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

    FRAMERATE = 33
    TIMESLICE = 1/FRAMERATE
    connections = {}

    @asyncio.coroutine
    def firehose(websocket, path, timeout=1):
        connections[websocket] = True
        frame = 0
        t1 = datetime.now()
        while True:

            if video_buffer.frame > frame:
                logging.debug('websocket {} reserving frame {}'.format(websocket, video_buffer.frame))
                frame = video_buffer.frame
            else:
                frame = video_buffer.update()

            t2 = datetime.now()
            dt = (t2-t1).total_seconds()
            t1 = t2

            if (dt < TIMESLICE):
                yield from asyncio.sleep(TIMESLICE-dt)

            data = video_buffer.buffer.tobytes()

            try:
                msg = yield from websocket.send(data)
                status = yield from websocket.recv()
            except websockets.exceptions.InvalidState:
                logger.info('websocket_server closing connection')
                del connections[websocket]
                break


    logging.info("websockets serving on {}".format(server_address))
    firehose_server = websockets.serve(firehose, *server_address)
    loop.run_until_complete(firehose_server)
