#!/usr/bin/env python3

"""Runs an event loop, pushing the one dimensional RGB data from VideoBuffer.buffer over a serial
line to an Arduino waiting to map those values to a NeoPixel strip.
A thread also listens for incoming OSC messages to control the buffer"""

import argparse
import asyncio
from collections import OrderedDict
from datetime import datetime
import json
import logging
from queue import Queue
import serial
import threading
import time

import numpy as np

import fx
import keyframes as kf
from osc import OSCServer
import websocket_server
import midi

logging.basicConfig(level=logging.INFO)

N = 420
# N = 256
FRAMERATE = 30 # 26.8 is on the edge of glitching the neopixels on my 2010 MBP.  Just enough glitch to be tasty.
BAUDRATE = 460800
# BAUDRATE = 230400
# BAUDRATE = 115200

# try these in order until one opens
SERIAL_DEVS = (
    '/dev/tty.usbmodemfd141',
    '/dev/tty.usbmodemfd131',
    '/dev/tty.usbmodemfa141',
)

def open_serial():
    for dev in SERIAL_DEVS:
        try:
            s = serial.Serial(port=dev, baudrate=BAUDRATE, timeout=2)
            logging.info("Opened serial port {}".format(dev))
            return s
        except (serial.SerialException, OSError):
            logging.debug("Couldn't open serial port {}".format(dev))
    raise Exception("couldn't open any serial port, failing")


class VideoBuffer(object):
    buffer = np.zeros(N * 3, dtype=np.uint8)

    def __init__(self, N=N):
        self.N = N

    def set(self, n, c):
        """ set pixel n to color c (r,g,b)"""
        self.buffer[n * 3:(n + 1) * 3] = c
        self.dirty = True

    def keyframes(self, keyframes=None):
        """preempts other f/x running, plays back keyframes"""
        self.lock.acquire()
        keyframes = keyframes or kf.bass_nuke

        def dither_color(c1, c2, t):
            if t < 1 / FRAMERATE:
                return
            nsteps = t * FRAMERATE
            delta = np.subtract(c2, c1) / nsteps
            for i in range(int(FRAMERATE * t)):
                c1 = (c1 + delta).astype(np.uint8)
                yield c1
                time.sleep(1 / FRAMERATE)

        i = iter(keyframes)
        frame = next(i)
        for next_frame in i:
            mask, delay = frame
            next_mask, next_delay = next_frame
            for color in dither_color(mask, next_mask, delay):
                self.mask(color)
                self.write()
            frame = next_frame
        self.lock.release()


try:
    serial_f = open_serial()
except:
    logging.warn("no serial")
    serial_f = None

video_buffer = VideoBuffer()

layered_effects = OrderedDict()  # define later
midi_queue = Queue()


def osc_logger(*args):
    logging.debug(args)

@asyncio.coroutine
def write_video_buffer():
    while True:
        logging.debug("write_video_buffer cb")
        for key, effect in layered_effects.items():
            if effect.enabled:
                effect.update()

        serial_f.write(video_buffer.buffer)
        yield from asyncio.sleep(1.0 / FRAMERATE)

def main():
    layered_effects['background'] = fx.BackGround(video_buffer, color='')
    # layered_effects['wave'] = fx.Wave(video_buffer)
    # layered_effects['midi_note'] = fx.MidiNote(video_buffer)
    layered_effects['pointX'] = fx.PointFx(video_buffer, axis=0)
    layered_effects['pointY'] = fx.PointFx(video_buffer, axis=1)
    layered_effects['pointZ'] = fx.PointFx(video_buffer, axis=2)
    layered_effects['scanner'] = fx.LarsonScanner(video_buffer, scanners=(
        {'n1':20, 'n2':45},
        {'n1':150,'n2':170},
        {'n1':250,'n2':290},
        {'n1':360,'n2':400},
    ) )

    layered_effects['peak_meter'] = fx.PeakMeter(video_buffer, meters=(
        {'n1': 10, 'n2': 100, 'reverse': False},
        {'n1': 180, 'n2': 280, 'reverse': False},
        {'n1': 342, 'n2': 400, 'reverse': False},
    ))

    midi_thread = threading.Thread(target=midi.main,kwargs={'q':midi_queue})
    midi_thread.daemon = True
    midi_thread.start()

    # https://docs.python.org/3/library/asyncio-eventloops.html#mac-os-x
    import selectors

    # selector = selectors.SelectSelector()
    # loop = asyncio.SelectorEventLoop(selector)
    # asyncio.set_event_loop(loop)
    loop = asyncio.get_event_loop()
    websocket_server.serve(loop, video_buffer.buffer)

    osc_server = OSCServer(
        loop = loop,
        maps = (
            ('/metronome', layered_effects['scanner'].metronome),
            ('/audio/envelope', layered_effects['peak_meter'].envelope),
            # ('/color/sky', color_sky),
            # ('/bassnuke', video_buffer.keyframes),
            # ('/midi/note', layered_effects['midi_note'].set),
            ('/accxyz', layered_effects['pointX'].xyz),
            # ('/accxyz', layered_effects['pointY'].xyz),
            # ('/accxyz', layered_effects['pointZ'].xyz),
            # ('/1/fader1', layered_effects['background'].red),
            # ('/1/fader2',  layered_effects['background'].green),
            # ('/1/fader3',  layered_effects['background'].blue),
            ('/*', osc_logger),
        )
    )
    osc_server.serve()
    # loop.add_writer(serial_f.fileno(), write_video_buffer)
    loop.run_until_complete(write_video_buffer())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

if __name__ == "__main__":
    main()
