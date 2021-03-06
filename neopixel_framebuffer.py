#!/usr/bin/env python3

"""Runs an event loop, pushing the one dimensional RGB data from VideoBuffer.buffer over a serial
line to an Arduino waiting to map those values to a NeoPixel strip.
A thread also listens for incoming OSC messages to control the buffer"""

import argparse
import asyncio
from concurrent.futures import CancelledError
import functools
import json
import logging
import os
import operator
import random

from audio_input import input_audio_stream, callback_video_buffer
import curses_console as console
from exceptions import UserQuit, MainLoopError
import log
import fx
from osc import OSCServer
import serial_comms
from video_buffer import VideoBuffer
import websocket_server


N = 420

IDLE_TIME = 1/30

video_buffer = VideoBuffer(N, resolution=N*10, operator='sub')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="0.0.0.0", help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=37340, help="The port the OSC server to listening on")
    parser.add_argument("-v", "--verbose", action="store_true", help="be chatty")
    parser.add_argument("-n", "--no-console", action="store_true", help="disable console")
    return parser.parse_args()


def osc_logger(*args):
    logging.debug(args)


def scanners(n_scanners):
    scanners = []

    width = 1
    span = 0.05
    for i in range(n_scanners):
        r = random.random()
        g = random.random()
        b = random.random()
        scanner = {'p1': i*span,'p2': i*span+width, 'width': width, 'color': (r, g, b)}
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
    obj['operator'] = video_buffer.operator
    with open(CONFIG_FILE, 'w') as f:
        return json.dump(obj, f)


async def idle():
    frame = 0
    while True:
        if video_buffer.frame > frame:
            frame = video_buffer.frame
        else:
            frame = video_buffer.update()

        await asyncio.sleep(IDLE_TIME)


def halt():
    console.stop()
    for t in asyncio.Task.all_tasks():
        t.cancel()
        try:
            logging.exception(t.exception())
            raise t.exception()
        except Exception as e:
            pass


async def main_loop(coros):

    done, pending = await asyncio.wait(coros, return_when=asyncio.FIRST_EXCEPTION)
    for t in done:
        if t.exception():
            raise t.exception()
    halt()


def exception_handler(loop, ctx):
    print("\n¯\_(ツ)_/¯\n")
    logging.exception(ctx['exception'])
    halt()


def main():
    args = parse_args()
    level = args.verbose and logging.DEBUG or logging.INFO

    config = load_config()

    video_buffer.operator = config.get('operator', 'add')
    video_buffer.add_effect('clear', fx.Clear, enabled=config.get('clear', True))
    video_buffer.add_effect('background', fx.BackGround, color=[0, 0, 0], enabled=config.get('background', False))
    video_buffer.add_effect('fade', fx.FadeBackGround, enabled=config.get('fade', False))

    # video_buffer.add_effect('midi_note_spark_1', fx.MidiNoteSpark, nrange=(300,420), enabled=config.get('midi_note_spark_1', False))
    # video_buffer.add_effect('midi_note_spark_2', fx.MidiNoteSpark, nrange=(0,150), enabled=config.get('midi_note_spark_2', False))
    # video_buffer.add_effect('midi_note_spark_3', fx.MidiNoteSpark, nrange=(150,300), enabled=config.get('midi_note_spark_3', False))

    # video_buffer.add_effect('strobe', fx.Strobe, enabled=config.get('strobe', False))
    video_buffer.add_effect('noise', fx.Noise, enabled=config.get('noise', False))
    video_buffer.add_effect('wave', fx.Wave, enabled=config.get('wave', False))
    video_buffer.add_effect('creamsicle', fx.Creamsicle, enabled=config.get('creamsicle', False))

    # note_ranges = ((260,320), (300,340), (340,380), (380,420), (0,40),(40,80),(80,120),(120,160),)
    # note_ranges = ((340, 380), (340,420), (340,380), (380,420), (0,40),(40,80),(80,120),(120,160),)
    # note_ranges = ((0,0), (300,420),)

    # for i, note_range in enumerate(note_ranges):
    #     name = 'midi_note'+str(i)
    #     video_buffer.add_effect(name, fx.MidiNote, nrange=note_range, enabled=config.get(name, False))

    video_buffer.add_effect('midi_note', fx.MidiNote, nrange=(.5,0.8), enabled=config.get('midi_note', False))

    # video_buffer.add_effect('pointX', fx.PointFx, nrange=(360,420), enabled=True)
    # video_buffer.add_effect('pointY', fx.PointFx, nrange=(360,420), enabled=True)
    # video_buffer.add_effect('pointZ', fx.PointFx, nrange=(360,420), enabled=True)

    video_buffer.add_effect('scanner', fx.LarsonScanner, enabled=config.get('scanner', True), scanners=[
        {'p1': .9,'p2': .98, 'width': .025, 'color': (.8,.1,0.05)},
        {'p1': .6,'p2': .65, 'width': .015, 'color': (.1,.8,.05)},
        {'p1': .3,'p2': .4, 'width': .015, 'color': (.04,.2,1)},
        {'p1': .02,'p2': .1, 'width': .015, 'color': (1,.8,0)},
        ])
    # video_buffer.add_effect('peak_meter', fx.PeakMeter, enabled=config.get('peak_meter', False), meters=(

    #     {'n1': 60, 'n2': 120, 'reverse': True, 'color': (1,.5,0)},
    #     {'n1': 120, 'n2': 160, 'reverse': False, 'color': (1,.5,0)},

    #     {'n1': 160, 'n2': 214, 'reverse': True, 'color': (1,.5,0)},
    #     {'n1': 214, 'n2': 260, 'reverse': False, 'color': (1,.5,0)},

    #     {'n1': 260, 'n2': 332, 'reverse': True, 'color': (1,.5,0)},
    #     {'n1': 332, 'n2': 380, 'reverse': False, 'color': (1,.5,0)},

    #     {'n1': 320, 'n2': 420, 'reverse': True, 'color': (1,.5,0)},
    #     {'n1': 0, 'n2': 100, 'reverse': False, 'color': (1,.5,0)},
    # ))
    # video_buffer.add_effect('convolution', fx.Convolution, enabled=config.get('convolution', False))
    video_buffer.add_effect('yb&rgp', fx.YellowBlackAndRedGreenPurple, enabled=config.get('yb&rgp', False))
    video_buffer.add_effect('matrix', fx.Matrix, enabled=config.get('matrix', False))
    video_buffer.add_effect('camera_rot', fx.CameraRot, enabled=config.get('camera_rot', False))


    def toggle_fx(addr, state):
        logging.info(f"toggling : {addr} : {state}")
        x,y = map(lambda x: int(x)-1, addr.split('/')[2:])
        i = x + 7*y
        fx = list(video_buffer.effects.values())[i]
        logging.info(fx)
        fx.toggle()


    osc_maps = [
        ('/metronome', video_buffer.effects['scanner'].metronome),
        # ('/audio/envelope', video_buffer.effects['peak_meter'].envelope),
        ('/midi/note', video_buffer.effects['midi_note'].set),
        ('/q', video_buffer.effects['fade'].set), # /fade or /fader cause bugs in touchosc, awesome
        ('/color/r', functools.partial(video_buffer.effects['background'].set, color='r')),
        ('/color/g', functools.partial(video_buffer.effects['background'].set, color='g')),
        ('/color/b', functools.partial(video_buffer.effects['background'].set, color='b')),
        ('/brightness', video_buffer.set_brightness),
        ('/gamma', video_buffer.set_gamma),
        ('/operator/*', video_buffer.set_operator, True),
        ('/fx/*', toggle_fx),
        ('/*', osc_logger)
    ]

    console_coros = ()
    if args.no_console:
        log.configure_logging(level=level)
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    else:
        osc_maps.append(('/*', console.osc_recv))
        log.configure_logging(level=level, queue_handler=True)
        console_coros = console.init(video_buffer)

    osc_server = OSCServer(
        maps = osc_maps,
        server_address = (args.ip, args.port)
    )
    serial_comms.init(video_buffer)
    coros = (
        osc_server.serve(),
        idle(),
        *console_coros,
        websocket_server.serve(video_buffer)
        # input_audio_stream(functools.partial(callback_video_buffer, video_buffer=video_buffer))
    )

    try:
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(exception_handler)
        loop.run_until_complete(main_loop(coros))

    except (KeyboardInterrupt, CancelledError, UserQuit) as e:
        print("have a great day")
    except MainLoopError as e:
        print("whooops")
    finally:
        loop.close()
        save_config()


if __name__ == "__main__":
    main()
