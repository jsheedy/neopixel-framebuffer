import asyncio
from datetime import datetime
import logging

import websockets


logger = logging.getLogger('websockets.server')

connections = {}

def osc_recv(datagram):
    """ handler for incoming OSC message """
    for k, q in connections.items():
        if not q:
            continue
        try:
            q.put_nowait(datagram)
        except asyncio.QueueFull:
            logger.warn('queue full for key {}'.format(k))

def osc_send(arguments):
    """ handler for outgoing OSC message """
    pass

def serve(loop, video_buffer, server_address=('0.0.0.0', 8766)):

    FRAMERATE = 20
    TIMESLICE = 1/FRAMERATE

    def firehose():
        frame = 0
        while True:
            if video_buffer.frame > frame:
                frame = video_buffer.frame
            else:
                frame = video_buffer.update()

            data = video_buffer.buffer.tobytes()
            yield data

    async def router(websocket, path):
        logger.info('new websocket connection: ' + str(id(websocket)))
        try:
            if path == "/firehose":
                connections[id(websocket)] = False
                t1 = datetime.now()
                for data in firehose():
                    msg = await websocket.send(data)

                    t2 = datetime.now()
                    dt = (t2-t1).total_seconds()
                    t1 = t2

                    if (dt < TIMESLICE):
                        await asyncio.sleep(TIMESLICE-dt)

            elif path == "/osc":
                q = asyncio.Queue(maxsize=2, loop=loop) # , loop=loop)
                connections[id(websocket)] = q

                while True:
                    try:
                        data = await q.get()
                        msg = await websocket.send(data)
                    except asyncio.queues.QueueEmpty:
                        logger.info('queue empty')
            else:
                logger.warn('unsupported websocket path')

        except (websockets.exceptions.InvalidState,
            websockets.exceptions.ConnectionClosed):
            logger.info('websocket_server closing connection')
        except Exception as e:
            logger.exception('websocket_server unhandled exception')
        finally:
            del connections[id(websocket)]

    logging.info("websockets serving on {}".format(server_address))
    server = websockets.serve(router, *server_address)
    loop.run_until_complete(server)
