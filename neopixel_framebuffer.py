#!/usr/bin/env python3

"""Runs an event loop, pushing the one dimensional RGB data from VideoBuffer.buffer over a serial
line to an Arduino waiting to map those values to a NeoPixel strip.
A thread also listens for incoming OSC messages to control the buffer"""

import argparse
from datetime import datetime
import itertools
import math
import random
import serial
import threading
import time

import numpy as np

import fx
from osc import OSCServer

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
            print("opened %s, read: %s" % (dev,x))
            return s
        except (serial.SerialException, OSError):
            print(dev + " didn't open")


class VideoBuffer(object):
    buffer = np.zeros(N*3, dtype=np.uint8)
    lock = threading.Lock()
    dirty = True
    
    def __init__(self, serial=None, N=N):
        self.serial = serial
        self.N=N
    
    def set(self, n, c):
        """ set pixel n to color c (r,g,b)"""
        # self.lock.acquire()
        self.buffer[n*3:(n+1)*3] = c
        self.dirty = True
        # self.lock.release()
        
    def write(self):
        self.lock.acquire()
        self.serial.write(self.buffer)
        self.dirty = False
        self.lock.release()

    def white_mask(self):
        self.buffer[0:N*3] = 255
        self.dirty = True

    def red_mask(self):
        self.black_mask()
        self.buffer[0:N*3:3] = 155
        self.dirty = True

    def green_mask(self):
        self.black_mask()
        self.buffer[1:N*3:3] = 155
        self.dirty = True

    def blue_mask(self):
        self.black_mask()
        self.buffer[2:(N*3):3] = 55
        self.dirty = True

    def black_mask(self):
        self.buffer[0:N*3] = 0
        self.dirty = True

    def strobe(self):
        """preempts other f/x running, to get a sweet strobe"""
        self.lock.acquire()
        self.white_mask()
        self.serial.write(self.buffer)
        # time.sleep(0.50)
        for delay in (.4,.2,.1,.05,.05):
            self.white_mask()
            self.serial.write(self.buffer)
            time.sleep(.05)
            self.black_mask()
            self.serial.write(self.buffer)
            time.sleep(delay)
        self.lock.release() 


video_buffer = VideoBuffer(serial=open_serial())

stop_event = threading.Event()

scanner = fx.LarsonScanner(video_buffer)
peak_meter = fx.PeakMeter(video_buffer, n1=220,n2=334,reverse=True)
peak_meter2 = fx.PeakMeter(video_buffer, n1=0,n2=120, reverse=False)
background = fx.BackGround(video_buffer)

layered_effects = []

def update_buffer():
    for effect in layered_effects:
        effect.update()

def write_video_buffer():
    while True:
        update_buffer()

        if stop_event.isSet():
            print("exiting")
            break
        if video_buffer.dirty:
            video_buffer.write()
        time.sleep(1.0 / FRAMERATE )

def demo():
    print("red")
    video_buffer.red_mask()
    time.sleep(.5)
    print("green")
    video_buffer.green_mask()
    time.sleep(.5)
    print("blue")
    video_buffer.blue_mask()
    time.sleep(.5)
    video_buffer.strobe()
    stop_event.set()

if __name__=="__main__":
    thread = threading.Thread(target=write_video_buffer)
    thread.start()

    parser = argparse.ArgumentParser(description='desc')
    parser.add_argument('--demo', action='store_true')
    args = parser.parse_args()

    if args.demo:
        demo()
    else:
        layered_effects = [
            background,
            scanner,
            peak_meter,
            peak_meter2
        ]
    
        osc_server = OSCServer(
            video_buffer=video_buffer,
            background=background,
            peak_meter=peak_meter,
            peak_meter2=peak_meter2,
            scanner=scanner
        )
        osc_server.serve()
