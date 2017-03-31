#!/usr/bin/env python3

"""Runs an event loop, pushing the one dimensional RGB data from VideoBuffer.buffer over a serial
line to an Arduino waiting to map those values to a NeoPixel strip.
A thread also listens for incoming OSC messages to control the buffer"""

import argparse
import asyncio
import json
import logging
import os
import random

import log
import curses_console as console
import fx
from osc import OSCServer
import serial_comms
# from touch_osc import accxyz
from video_buffer import VideoBuffer
import websocket_server

from audio_input_callback import input_audio_stream

N = 420

video_buffer = VideoBuffer(N)

# input_audio_stream(video_buffer)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="0.0.0.0", help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=37340, help="The port the OSC server to listening on")
    parser.add_argument("-v", "--verbose", action="store_true", help="be chatty")
    parser.add_argument("-n", "--noconsole", action="store_true", help="disable console")
    return parser.parse_args()


def osc_logger(*args):
    logging.debug(args)


def scanners(n_scanners):
    scanners = []

    span = video_buffer.N // n_scanners
    width = 14
    for i in range(n_scanners):
        r = random.random()
        g = random.random()
        b = random.random()
        scanner = {'n1': i*span,'n2': i*span+width, 'width': random.randint(1,3), 'color': (r, g, b)}
        scanners.append(scanner)
    return scanners

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")


def load_config():
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except:
        return {}


def save_config():
    obj = {}
    for name, effect in video_buffer.effects.items():
        obj[name] = effect.enabled

    with open(CONFIG_FILE, 'w') as f:
        return json.dump(obj, f)


async def idle():
    frame = 0
    while True:
        if video_buffer.frame > frame:
            frame = video_buffer.frame
        else:
            frame = video_buffer.update()

        await asyncio.sleep(.05)


def main():
    args = parse_args()
    level = args.verbose and logging.DEBUG or logging.INFO

    config = load_config()

    video_buffer.add_effect('background', fx.BackGround, color=[0, 0, 255], enabled=config.get('background', False))
    video_buffer.add_effect('fade', fx.FadeBackGround, q=71, enabled=config.get('fade', False))
    video_buffer.add_effect('strobe', fx.Strobe, enabled=config.get('strobe', False))
    video_buffer.add_effect('noise', fx.Noise, enabled=config.get('noise', False))
    video_buffer.add_effect('wave', fx.Wave, enabled=config.get('wave', False))

    # note_ranges = (
    #     (0, 60), (61,120), (121, 170), (170, 220), (221, 280), (281, 331), (332, 379), (380, 420)
    # )
    note_ranges = ((260,320), (300,340), (340,380), (380,420), (0,40),(40,80),(80,120),(120,160),)
    for i, note_range in enumerate(note_ranges):
        name = 'midi_note'+str(i)
        video_buffer.add_effect(name, fx.MidiNote, nrange=note_range, enabled=config.get(name, False))

    # video_buffer.add_effect('pointX', fx.PointFx, nrange=(360,420), enabled=True)
    # video_buffer.add_effect('pointY', fx.PointFx, nrange=(360,420), enabled=True)
    # video_buffer.add_effect('pointZ', fx.PointFx, nrange=(360,420), enabled=True)

    video_buffer.add_effect('scanner', fx.LarsonScanner, enabled=config.get('scanner', False), scanners=scanners(12))
    video_buffer.add_effect('peak_meter', fx.PeakMeter, enabled=config.get('peak_meter', False), meters=(
        {'n1': 320, 'n2': 420, 'reverse': True, 'color': (1,.5,0)},
        {'n1': 0, 'n2': 100, 'reverse': False, 'color': (0,.5,1)},
    ))
    video_buffer.add_effect('brightness', fx.Brightness, level=0.4, enabled=config.get('brightness', False))
    video_buffer.add_effect('convolution', fx.Convolution, enabled=config.get('convolution', False))

    def midi_handler(*args):
        addr, note, velocity, channel = args
        key = f'midi_note{channel}'
        video_buffer.effects[key].set(*args)

    maps = [
        ('/metronome', video_buffer.effects['scanner'].metronome),
        ('/metronome', video_buffer.effects['strobe'].metronome),
        ('/audio/envelope', video_buffer.effects['peak_meter'].envelope),
        ('/midi/note', midi_handler),
        ('/midi/cc', video_buffer.effects['background'].set),
        # ('/accxyz', functools.partial(accxyz, axis=0, point=effects['pointX'])),
    ]

    loop = asyncio.get_event_loop()

    if args.noconsole:
        maps.append(('/*', osc_logger))
        log.configure_logging(level=level)

    else:
        maps.append(('/*', console.osc_recv))
        log.configure_logging(level=level, queue_handler=True)
        console.init(loop, video_buffer)

    osc_server = OSCServer(
        loop = loop,
        maps = maps,
        forward = (websocket_server.osc_recv, ),
        server_address = (args.ip, args.port)
    )

    websocket_server.serve(loop, video_buffer)
    serial_comms.init(loop, video_buffer)
    osc_server.serve()
    asyncio.ensure_future(idle())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info("keyboard int")
    finally:
        loop.close()
        save_config()


if __name__ == "__main__":
    main()
