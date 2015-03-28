#!/usr/bin/env python3

"""Runs an event loop, pushing the one dimensional RGB data from VideoBuffer.buffer over a serial
line to an Arduino waiting to map those values to a NeoPixel strip.
A thread also listens for incoming OSC messages to control the buffer"""

import argparse
import asyncio
from collections import OrderedDict
import json
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
FRAMERATE = 24 # 26
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
            s = serial.Serial(port=dev, baudrate=BAUDRATE, timeout=20)
            x = s.readline()
            print("opened %s, read: %s" % (dev, x))
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
        # self.lock.acquire()
        self.buffer[n * 3:(n + 1) * 3] = c
        self.dirty = True
        # self.lock.release()

    def write(self):
#         self.lock.acquire()
        # for output in self.outputs:
        #     output.write(self.buffer)
        self.dirty = False
#         self.lock.release()

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

        sleep_latency_factor = .5  # our framerate isn't actual framerate due to arduino latency et all.  should calculate it!
        def dither_color(c1, c2, t):
            if t < 1 / FRAMERATE:
                return
            nsteps = t * FRAMERATE
            delta = np.subtract(c2, c1) / nsteps
            for i in range(int(FRAMERATE * t)):
                c1 = (c1 + delta).astype(np.uint8)
                print(c1)
                yield c1
                time.sleep(1 / FRAMERATE + .02)

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

class ConsoleLogger():
    def write(self, bytes):
        print(bytes)

logger = ConsoleLogger()
try:
    serial_f = open_serial()
except:
    print("no serial")
    serial_f = None

video_buffer = VideoBuffer(outputs=[])
# video_buffer = VideoBuffer(outputs=[])
# video_buffer = VideoBuffer(outputs=[logger])
# video_buffer = VideoBuffer(outputs=[open_serial(), websocket])

stop_event = threading.Event()

layered_effects = OrderedDict()  # define later
midi_queue = Queue()
ws_event = threading.Event()

def write_video_buffer():
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
        # if video_buffer.dirty:
        if serial_f:
            serial_f.write(video_buffer.buffer)
        ws_event.set()
        # ws_queue.put(json.dumps(video_buffer.buffer.tolist()))
        time.sleep(1.0 / FRAMERATE)

def demo():
    video_buffer.keyframes(kf.rgb)
    stop_event.set()

if __name__ == "__main__":
    video_buffer_thread = threading.Thread(target=write_video_buffer)
    video_buffer_thread.daemon = True
    video_buffer_thread.start()

    parser = argparse.ArgumentParser(description='desc')
    parser.add_argument('--demo', action='store_true')
    args = parser.parse_args()
    if args.demo:
        demo()
    else:
        # layered_effects['background'] = fx.BackGround(video_buffer)
        layered_effects['wave'] = fx.Wave(video_buffer)
        # layered_effects['midi_note'] = fx.MidiNote(video_buffer)
        # layered_effects['scanner'] = fx.LarsonScanner(video_buffer, n1=0, n2=255)
        # layered_effects['peak_meter'] = fx.PeakMeter(video_buffer, n1=100, n2=120, reverse=False)
        # layered_effects['peak_meter2'] = fx.PeakMeter(video_buffer, n1=200, n2=220, reverse=False)

        midi_thread = threading.Thread(target=midi.main,kwargs={'q':midi_queue})
        midi_thread.daemon = True
        midi_thread.start()
        loop = asyncio.get_event_loop()
        websocket_thread = threading.Thread(target=websocket_server.serve, args=(loop, ws_event, video_buffer.buffer))
        websocket_thread.daemon = True
        websocket_thread.start()

        osc_server = OSCServer(
            video_buffer=video_buffer,
            effects=layered_effects
        )
        osc_server.serve()
