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

    video_buffer.add_effect('background', fx.BackGround, color=[20, 10, 40], enabled=False)
    video_buffer.add_effect('fade', fx.FadeBackGround, q=2, enabled=False)
    video_buffer.add_effect('strobe', fx.Strobe, enabled=False)
    video_buffer.add_effect('noise', fx.Noise, enabled=False)
    video_buffer.add_effect('wave', fx.Wave, enabled=False)

    note_ranges = (
        (0, 60), (61,120), (121, 170), (170, 220), (221, 280), (281, 331), (332, 379), (380, 420)
    )
    for i, note_range in enumerate(note_ranges):
        video_buffer.add_effect('midi_note'+str(i), fx.MidiNote, nrange=note_range, enabled=True)

    # video_buffer.add_effect('pointX', fx.PointFx, nrange=(360,420), enabled=True)
    # video_buffer.add_effect('pointY', fx.PointFx, nrange=(360,420), enabled=True)
    # video_buffer.add_effect('pointZ', fx.PointFx, nrange=(360,420), enabled=True)

    video_buffer.add_effect('scanner', fx.LarsonScanner, enabled=False, scanners=scanners(10))
    video_buffer.add_effect('peak_meter', fx.PeakMeter, enabled=False, meters=(
        {'n1': 320, 'n2': 420, 'reverse': True, 'color': (1,.5,0)},
        {'n1': 0, 'n2': 100, 'reverse': False, 'color': (0,.5,1)},
    ))
    video_buffer.add_effect('brightness', fx.Brightness, level=0.4, enabled=False)
    video_buffer.add_effect('convolution', fx.Convolution, enabled=True)

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
            ('/midi/note', video_buffer.effects['midi_note0'].set),
            ('/midi/note', video_buffer.effects['midi_note1'].set),
            ('/midi/note', video_buffer.effects['midi_note2'].set),
            ('/midi/note', video_buffer.effects['midi_note3'].set),
            ('/midi/note', video_buffer.effects['midi_note4'].set),
            ('/midi/note', video_buffer.effects['midi_note5'].set),
            ('/midi/note', video_buffer.effects['midi_note6'].set),
            ('/midi/note', video_buffer.effects['midi_note7'].set),
            ('/midi/cc', video_buffer.effects['background'].set),
            # ('/accxyz', functools.partial(accxyz, axis=0, point=effects['pointX'])),
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
