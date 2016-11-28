#!/usr/bin/env python3

"""Runs an event loop, pushing the one dimensional RGB data from VideoBuffer.buffer over a serial
line to an Arduino waiting to map those values to a NeoPixel strip.
A thread also listens for incoming OSC messages to control the buffer"""

import argparse
import asyncio
import logging
from queue import Queue
import random

import console
import fx
from osc import OSCServer
import serial_comms
# from touch_osc import accxyz
from video_buffer import VideoBuffer
import websocket_server

from audio_input_callback import input_audio_stream

N = 420

video_buffer = VideoBuffer(N)
midi_queue = Queue()

# input_audio_stream(video_buffer)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="0.0.0.0", help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=37340, help="The port the OSC server to listening on")
    parser.add_argument("-v", "--verbose", action="store_true", help="be chatty")
    return parser.parse_args()


def osc_logger(*args):
    logging.debug(args)


def scanners(n_scanners):
    scanners = []

    width = video_buffer.N // n_scanners
    for i in range(n_scanners):
        r = random.random()
        g = random.random()
        b = random.random()
        scanner = {'n1': i*width,'n2': i*width+width, 'width': random.randint(1,5), 'color': (r, g, b)}
        scanners.append(scanner)
    return scanners


def main():
    args = parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # effects['background'] = fx.BackGround(video_buffer, color='')
    video_buffer.add_effect('fade', fx.FadeBackGround, q=25, enabled=True)
    video_buffer.add_effect('strobe', fx.Strobe, enabled=False)
    video_buffer.add_effect('noise', fx.Noise, enabled=False)
    video_buffer.add_effect('wave', fx.Wave, enabled=False)
    video_buffer.add_effect('midi_note', fx.MidiNote, range=(300, 420), enabled=False)
    # add_effect('pointX'] = fx.PointFx(video_buffer, range=(360,420))
    # add_effect('pointY'] = fx.PointFx(video_buffer)
    # add_effect('pointZ'] = fx.PointFx(video_buffer)
    video_buffer.add_effect('scanner', fx.LarsonScanner, enabled=False, scanners=scanners(10))
    video_buffer.add_effect('peak_meter', fx.PeakMeter, enabled=True, meters=(
        {'n1': 320, 'n2': 420, 'reverse': True, 'color': (1,.5,0)},
        {'n1': 0, 'n2': 100, 'reverse': False, 'color': (0,.5,1)},
    ))
    video_buffer.add_effect('brightness', fx.Brightness, enabled=False)
    video_buffer.add_effect('convolution', fx.Convolution, enabled=True)

    # midi_thread = threading.Thread(target=midi.main,kwargs={'q':midi_queue})
    # midi_thread.daemon = True
    # midi_thread.start()

    loop = asyncio.get_event_loop()

    console.init(loop, video_buffer)
    websocket_server.serve(loop, video_buffer)
    serial_comms.init(loop, video_buffer)

    osc_server = OSCServer(
        loop = loop,
        maps = (
            ('/metronome', video_buffer.effects['scanner'].metronome),
            ('/metronome', video_buffer.effects['strobe'].metronome),
            ('/audio/envelope', video_buffer.effects['peak_meter'].envelope),
            ('/midi/note', video_buffer.effects['midi_note'].set),
            # ('/accxyz', functools.partial(accxyz, axis=0, point=effects['pointX'])),
            # ('/1/fader1', effects['background'].red),
            # ('/1/fader2',  effects['background'].green),
            # ('/1/fader3',  effects['background'].blue),
            ('/*', osc_logger),
        ),
        forward = (websocket_server.osc_recv, ),
        server_address = (args.ip, args.port)
    )

    osc_server.serve()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info("keyboard int")
    finally:
        loop.close()

if __name__ == "__main__":
    main()
