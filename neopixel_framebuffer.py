#!/usr/bin/env python3

"""Runs an event loop, pushing the one dimensional RGB data from VideoBuffer.buffer over a serial
line to an Arduino waiting to map those values to a NeoPixel strip.
A thread also listens for incoming OSC messages to control the buffer"""

import argparse
import asyncio
from collections import OrderedDict
from datetime import datetime
import functools
import json
import logging
from queue import Queue
import serial
import sys
import threading
import time

import numpy as np

import fx
import keyframes as kf
from osc import OSCServer
from touch_osc import accxyz
import websocket_server
import midi

logging.basicConfig(level=logging.INFO)


N = 420
FRAMERATE = 25 # 26.8 is on the edge of glitching the neopixels on my 2010 MBP.  Just enough glitch to be tasty.
# FRAMERATE = 26 # 26.8 is on the edge of glitching the neopixels on my 2010 MBP.  Just enough glitch to be tasty.
# BAUDRATE = 9600
BAUDRATE = 460800
# BAUDRATE = 230400
# BAUDRATE = 115200

# try these in order until one opens
SERIAL_DEVS = (
    '/dev/tty.usbmodem1451',
    '/dev/tty.usbmodemfd141',
    '/dev/tty.usbmodem1411',
    '/dev/tty.usbmodemfd131',
    '/dev/tty.usbmodemfa141',
)

def open_serial():
    for dev in SERIAL_DEVS:
        try:
            s = serial.Serial(port=dev, baudrate=BAUDRATE, timeout=2)
            logging.info("Opened serial port {}".format(dev))
            # flush buffers
            # while(s.inWaiting() == 0):
            #     s.write(0)

            return s
        except (serial.SerialException, OSError):
            logging.warn("Couldn't open serial port {}".format(dev))
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

video_buffer = VideoBuffer()

layered_effects = OrderedDict()  # define later
midi_queue = Queue()


def osc_logger(*args):
    logging.debug(args)

@asyncio.coroutine
def update_video_buffer():
    while True:
        for key, effect in layered_effects.items():
            if effect.enabled:
                effect.update()
        yield from asyncio.sleep(1.0 / FRAMERATE)

serial_f = None
try:
    serial_f = open_serial()
except:
    logging.warn("no serial")

def write_serial():
    status = serial_f.read(serial_f.inWaiting())
    serial_f.write(video_buffer.buffer.tobytes())

def read_stdin():
    line = sys.stdin.readline().strip()
    fx = layered_effects.get(line)
    if fx:
        fx.toggle()
        logging.info('toggled f/x {} {}'.format(fx, fx.enabled))
    elif line[:4] == 'fade':
        _, fade_amount = line.split()
        fade = layered_effects['fade']
        fade.q = int(fade_amount)
    else:
        logging.info('unknown f/x {}'.format(line))
    print('all f/x:')

    print('{0:20} enabled'.format('f/x'))
    print('-'*30)
    for fx in layered_effects.keys():
        print('{0:20} {1}'.format(fx, layered_effects[fx].enabled))


def main():
    # layered_effects['background'] = fx.BackGround(video_buffer, color='')
    layered_effects['fade'] = fx.FadeBackGround(video_buffer, q=15)
    layered_effects['wave'] = fx.Wave(video_buffer, enabled=False)
    layered_effects['midi_note'] = fx.MidiNote(video_buffer, range=(310, 410))
    # layered_effects['pointX'] = fx.PointFx(video_buffer, range=(360,420))
    # layered_effects['pointY'] = fx.PointFx(video_buffer)
    # layered_effects['pointZ'] = fx.PointFx(video_buffer)
    layered_effects['scanner'] = fx.LarsonScanner(video_buffer, enabled=True, scanners=(
        {'n1':20, 'n2':45},
        {'n1':150,'n2':170},
        {'n1':250,'n2':290},
        # {'n1':360,'n2':400},
    ) )
    layered_effects['peak_meter'] = fx.PeakMeter(video_buffer, enabled=True, meters=(
        {'n1': 340, 'n2': 420, 'reverse': True},
        {'n1': 0, 'n2': 100, 'reverse': False},
    ))

    # midi_thread = threading.Thread(target=midi.main,kwargs={'q':midi_queue})
    # midi_thread.daemon = True
    # midi_thread.start()

    loop = asyncio.get_event_loop()
    # loop.set_debug(True)

    websocket_server.serve(loop, video_buffer.buffer)

    osc_server = OSCServer(
        loop = loop,
        maps = (
            ('/metronome', layered_effects['scanner'].metronome),
            ('/audio/envelope', layered_effects['peak_meter'].envelope),
            # ('/bassnuke', video_buffer.keyframes),
            ('/midi/note', layered_effects['midi_note'].set),
            # ('/accxyz', functools.partial(accxyz, axis=0, point=layered_effects['pointX'])),
            # ('/1/fader1', layered_effects['background'].red),
            # ('/1/fader2',  layered_effects['background'].green),
            # ('/1/fader3',  layered_effects['background'].blue),
            ('/*', osc_logger),
        )
    )
    osc_server.serve()

    loop.create_task(update_video_buffer())
    if serial_f:
        loop.add_reader(serial_f.fileno(), write_serial)
    loop.add_reader(sys.stdin.fileno(), read_stdin)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

if __name__ == "__main__":
    main()
