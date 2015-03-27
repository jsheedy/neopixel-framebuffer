import asyncio
import json
import random
import time

import websockets

def serve(loop, event, video_buffer):

    @asyncio.coroutine
    def firehose(websocket, path, timeout=1):
        while True:
            event.wait()
            if not websocket.open:
                print("BREAK")
                break
            # data = json.dumps(video_buffer.tolist())

            data = video_buffer.tostring()
            try:
                msg = yield from websocket.send(data)
            except:
                print("BROKEN")
                break
            event.clear()


    asyncio.set_event_loop(loop)
    firehose_server = websockets.serve(firehose, 'localhost', 8766)
    asyncio.get_event_loop().run_until_complete(firehose_server)
    asyncio.get_event_loop().run_forever()