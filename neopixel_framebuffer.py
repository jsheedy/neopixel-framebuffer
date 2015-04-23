#!/usr/bin/env python3

"""Runs an event loop, pushing the one dimensional RGB data from VideoBuffer.buffer over a serial
line to an Arduino waiting to map those values to a NeoPixel strip.
A thread also listens for incoming OSC messages to control the buffer"""

import argparse
import asyncio
from collections import OrderedDict
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

N = 420
# N = 256
FRAMERATE = 26.8 # 26.8 is on the edge of glitching the neopixels on my 2010 MBP.  Just enough glitch to be tasty.
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
            return s
        except (serial.SerialException, OSError):
            print(dev + " didn't open")
    raise Exception("couldn't open any serial port, failing")


class VideoBuffer(object):
    buffer = np.zeros(N * 3, dtype=np.uint8)
    lock = threading.Lock()
    dirty = True

    def __init__(self, outputs=None, N=N):
        self.outputs = outputs
        self.N = N

    def set(self, n, c):
        """ set pixel n to color c (r,g,b)"""
        self.buffer[n * 3:(n + 1) * 3] = c
        self.dirty = True

    def write(self):
        self.dirty = False

    def mask(self, mask):
        self.buffer[0:N * 3] = np.tile(mask, N)
        self.dirty = True

    def white_mask(self):
        self.buffer[0:N * 3] = 255
        self.dirty = True

    def red_mask(self):
        self.black_mask()
        self.buffer[0:N * 3:3] = 155
        self.dirty = True

    def green_mask(self):
        self.black_mask()
        self.buffer[1:N * 3:3] = 155
        self.dirty = True

    def blue_mask(self):
        self.black_mask()
        self.buffer[2:(N * 3):3] = 55
        self.dirty = True

    def black_mask(self):
        self.buffer[0:N * 3] = 0
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

    def strobe(self):
        """preempts other f/x running, to get a sweet strobe"""
        self.lock.acquire()
        for delay in (.4, .2, .1, .05, .05):
            self.white_mask()
            self.write()
            time.sleep(.05)
            self.black_mask()
            self.write()
            time.sleep(delay)
        self.lock.release()

# class ConsoleLogger():
#     def write(self, bytes):
#         print(bytes)

# logger = ConsoleLogger()
try:
    serial_f = open_serial()
except:
    print("no serial")
    serial_f = None

video_buffer = VideoBuffer(outputs=[])
# video_buffer = VideoBuffer(outputs=[])
# video_buffer = VideoBuffer(outputs=[logger])

stop_event = threading.Event()

layered_effects = OrderedDict()  # define later
midi_queue = Queue()

def write_video_buffer():
    from fx import Wave
    while True:
        x = not midi_queue.empty() and midi_queue.get(False)
        for key, effect in layered_effects.items():
            if x and x.get('key')==key:
                layered_effects[key].enabled=x.get('value')

            if effect.enabled:
                effect.update()

        if stop_event.isSet():
            print("exiting")
            break
        if serial_f:
            serial_f.write(video_buffer.buffer)
        time.sleep(1.0 / FRAMERATE)

def demo():
    meter = fx.PeakMeter(video_buffer, meters=(
                {'n1': 342, 'n2': 400, 'reverse': False},
            ))
    for f in range(1000):
        meter.meters[0].set(f/1000.0)
        meter.update()
        time.sleep(.02)
    # video_buffer.keyframes(kf.rgb)
    stop_event.set()

def main():
    video_buffer_thread = threading.Thread(target=write_video_buffer)
    video_buffer_thread.daemon = True
    video_buffer_thread.start()

    parser = argparse.ArgumentParser(description='desc')
    parser.add_argument('--demo', action='store_true')
    args = parser.parse_args()
    if args.demo:
        demo()
    else:
        layered_effects['background'] = fx.BackGround(video_buffer, color='')
        # layered_effects['wave'] = fx.Wave(video_buffer)
        layered_effects['midi_note'] = fx.MidiNote(video_buffer)
        layered_effects['pointX'] = fx.PointFx(video_buffer, axis=0)
        layered_effects['pointY'] = fx.PointFx(video_buffer, axis=1)
        layered_effects['pointZ'] = fx.PointFx(video_buffer, axis=2)
        # layered_effects['scanner'] = fx.LarsonScanner(video_buffer, scanners=(
        #     {'n1':20, 'n2':45},
        #     {'n1':150,'n2':170},
        #     {'n1':250,'n2':290},
        #     # {'n1':360,'n2':400},
        # ) )

        layered_effects['peak_meter'] = fx.PeakMeter(video_buffer, meters=(
            # {'n1': 10, 'n2': 100, 'reverse': False},
            # {'n1': 180, 'n2': 280, 'reverse': False},
            {'n1': 342, 'n2': 400, 'reverse': False},
        ))

        midi_thread = threading.Thread(target=midi.main,kwargs={'q':midi_queue})
        midi_thread.daemon = True
        midi_thread.start()

        loop = asyncio.get_event_loop()
        websocket_thread = threading.Thread(target=websocket_server.serve, args=(loop, video_buffer.buffer))
        websocket_thread.daemon = True
        websocket_thread.start()

        osc_queue = Queue()

        def osc_queuer(*args):
            print(args,)
            # logging.info(msg)
            # osc_queue.put(msg)

        def color_sky(self, name, channel, r,g,b):
            layered_effects['background'].red(r)
            layered_effects['background'].green(g)
            layered_effects['background'].blue(b)

        osc_server = OSCServer(
            maps = (
                # ('/metronome', layered_effects['scanner'].metronome),
                # ('/audio/envelope', layered_effects['peak_meter'].envelope),
                ('/color/sky', color_sky),
                ('/bassnuke', video_buffer.keyframes),
                ('/midi/note', layered_effects['midi_note'].set),
                ('/accxyz', layered_effects['pointX'].xyz),
                ('/accxyz', layered_effects['pointY'].xyz),
                ('/accxyz', layered_effects['pointZ'].xyz),
                # ('/1/fader1', layered_effects['background'].red),
                # ('/1/fader2',  layered_effects['background'].green),
                # ('/1/fader3',  layered_effects['background'].blue),
                # ('/*', osc_queuer),
            )
        )
        osc_server.serve()

if __name__ == "__main__":
    main()
