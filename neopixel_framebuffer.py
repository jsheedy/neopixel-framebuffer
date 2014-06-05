#!/usr/bin/env python3

"""Runs an event loop, pushing the one dimensional RGB data from VideoBuffer.buffer over a serial
line to an Arduino waiting to map those values to a NeoPixel strip.
A thread also listens for incoming OSC messages to control the buffer"""

import argparse
from collections import OrderedDict
from datetime import datetime
import itertools
import math
from queue import Queue
import random
import serial
import threading
import time

import numpy as np

import fx
import keyframes as kf
from osc import OSCServer
import midi

N = 420
FRAMERATE = 26
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
        for output in self.outputs:
            output.write(self.buffer)
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

#         self.white_mask()
#         self.write()
        # time.sleep(0.50)
        for delay in (.4, .2, .1, .05, .05):
            self.white_mask()
            self.write()
            time.sleep(.05)
            self.black_mask()
            self.write()
            time.sleep(delay)
        self.lock.release() 

class WebSocket(object):
    def write(self, bytes):
        pass
websocket = WebSocket()

video_buffer = VideoBuffer(outputs=[open_serial()])
# video_buffer = VideoBuffer(outputs=[open_serial(), websocket])

stop_event = threading.Event()

layered_effects = OrderedDict()  # define later
queue = Queue()
x=None
def write_video_buffer():
    while True:
        x = not queue.empty() and queue.get(False)
        for key, effect in layered_effects.items():
            if x and x.get('key')==key:
                layered_effects[key].enabled=x.get('value')
            if effect.enabled:
                effect.update()

        if stop_event.isSet():
            print("exiting")
            break
        if video_buffer.dirty:
            video_buffer.write()
        time.sleep(1.0 / FRAMERATE)

def demo():
    video_buffer.keyframes(kf.rgb)
    stop_event.set()


if __name__ == "__main__":
    thread = threading.Thread(target=write_video_buffer)
    thread.start()

    parser = argparse.ArgumentParser(description='desc')
    parser.add_argument('--demo', action='store_true')
    args = parser.parse_args()
    if args.demo:
        demo()
    else:
        layered_effects['background'] = fx.BackGround(video_buffer)
        layered_effects['wave'] = fx.Wave(video_buffer)
        layered_effects['scanner'] = fx.LarsonScanner(video_buffer)
        layered_effects['peak_meter'] = fx.PeakMeter(video_buffer, n1=220, n2=334, reverse=True)
        layered_effects['peak_meter2'] = fx.PeakMeter(video_buffer, n1=0, n2=120, reverse=False)

        midi_thread = threading.Thread(target=midi.main,kwargs={'q':queue})
        midi_thread.start()

        osc_server = OSCServer(
            video_buffer=video_buffer,
            effects=layered_effects
        )
        osc_server.serve()
