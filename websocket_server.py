import asyncio
import websockets
import time
import random

# class WebSocketServer():


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

def serve(loop):
    asyncio.set_event_loop(loop)
    firehose_server = websockets.serve(firehose, 'localhost', 8766)
    asyncio.get_event_loop().run_until_complete(firehose_server)
    asyncio.get_event_loop().run_forever()
    print("WS SERVE")