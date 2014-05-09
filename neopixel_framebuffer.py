#!/usr/bin/env python3

import argparse
from datetime import datetime
import itertools
import math
import random
import serial
import threading
import time

import numpy as np

baud = 460800
# baud = 230400
# baud = 115200

devs = (
    '/dev/tty.usbmodemfd141', 
    '/dev/tty.usbmodemfd131',
    '/dev/tty.usbmodemfa141', 
)

for dev in devs:
    try:
        s = serial.Serial(port=dev, baudrate=baud, timeout=20)
        print(dev + " worked")
        break
    except (serial.SerialException, OSError):
        print(dev + " didn't work")
    
x = s.readline()
print("read %s" % x)

N = 420
FRAMERATE = 26

class VideoBuffer(object):
    buffer = np.zeros(N*3, dtype=np.uint8)
    lock = threading.Lock()
    dirty = True
    
    def set(self, n, c):
        """ set pixel n to color c (r,g,b)"""
        # self.lock.acquire()
        self.buffer[n*3:(n+1)*3] = c
        self.dirty = True
        # self.lock.release()
        
    def write(self):
        self.lock.acquire()
        s.write(self.buffer)
        self.dirty = False
        self.lock.release()

video_buffer = VideoBuffer()

def white_mask():
    video_buffer.buffer[0:N*3] = 255
    video_buffer.dirty = True

def red_mask():
    black_mask()
    video_buffer.buffer[0:N*3:3] = 55
    video_buffer.dirty = True

def blue_mask():
    black_mask()
    video_buffer.buffer[2:(N*3):3] = 55
    video_buffer.dirty = True

def black_mask():
    video_buffer.buffer[0:N*3] = 0
    video_buffer.dirty = True

stop_event = threading.Event()

class LarsonScanner(object):
    def __init__(self):
        self.n1 = 360
        self.n2 = 410
        self.pos = 380
        self.bpm = 120
        self.count = 1
        self.timestamp = datetime(2000,1,1)
        self.velocity = 2

    def metronome(self, bpm, count):
        self.timestamp = datetime.now()
        self.bpm = int(bpm)
        self.count = int(count)

    def update(self):
        
        if (datetime.now() - self.timestamp).seconds > 2:
            if self.pos >= self.n2-2:
                self.velocity = -2

            if self.pos <= self.n1+2:
                self.velocity = 2

            self.pos += self.velocity 
        else:

            secs = (datetime.now() - self.timestamp).total_seconds()
            delta_beat = secs / (60/self.bpm)
            if self.count in (1,3):
                self.pos = int(self.n1 + (self.n2 - self.n1) * delta_beat)
            else:
                self.pos = int(self.n2 - (self.n2 - self.n1) * delta_beat)

        if self.pos > self.n2:
            self.pos = self.n2-2
        if self.pos < self.n1:
            self.pos = self.n1

        video_buffer.buffer[self.pos*3:self.pos*3+3] = (255,0,0)
        video_buffer.buffer[(self.pos-1)*3:(self.pos-1)*3+3] = (35,0,0)
        video_buffer.buffer[(self.pos+1)*3:(self.pos+1)*3+3] = (35,0,0)
        video_buffer.dirty = True

scanner = LarsonScanner()

class BackGround(object):
    
    bgbuffer = np.zeros(N*3, dtype=np.uint8)

    def red(self, x):
        print(x)
        self.bgbuffer[0:N*3:3] = int(x*255)
    
    def green(self, x):
        self.bgbuffer[1:N*3:3] = int(x*255)

    def blue(self, x):
        self.bgbuffer[2:N*3:3] = int(x*255)

    def update(self):
        video_buffer.buffer = self.bgbuffer.copy()
        video_buffer.dirty = True

class Wave(object):
    
    pointer = itertools.cycle(range(N))
    
    # buff = np.zeros(N*3, dtype=np.uint8)
    buff = np.array( 255*np.sin(np.arange(0,420*N, dtype=np.uint8)) , dtype=np.uint8)

    def __init__(self, w=1, f=1):
        self.w=w
        self.f=f

    def update(self):
        i = next(self.pointer)
        video_buffer.buffer = self.buff# .copy()
        video_buffer.dirty = True

class PeakMeter(object):
    def __init__(self,n1=280, n2=320,reverse=False):
        self.n1 = n1
        self.n2 = n2
        self.reverse = reverse
        self.set(0)
        self.level = 0.0
    
    def set(self, level):
        """level 0 -> 1"""
        self.level = level

    def update(self):
        
        lev = int((self.n2 - self.n1) *.8 )
        y = int(self.level * (self.n2 - self.n1))
    
        if not self.reverse:
            video_buffer.buffer[self.n1*3:(self.n1+y)*3] = (0,155,0)*y
            # if (self.level > .8):
                # video_buffer.buffer[(self.n1+lev)*3:(self.n1+y)*3] = (255,0,0)*(y-lev)
        else:
            video_buffer.buffer[self.n2*3-1:(self.n2-y)*3-1:-1] = (0,155,0)*y
            # if (self.level > .8):
                # video_buffer.buffer[(self.n2+lev)*3:(self.n2+y)*3:-1] = (255,0,0)*(y-lev)

        video_buffer.dirty = True

peak_meter = PeakMeter(n1=220,n2=334,reverse=True)
peak_meter2 = PeakMeter(n1=0,n2=120, reverse=False)
background = BackGround()


def update_buffer():
    background.update()
    scanner.update()
    peak_meter.update()
    peak_meter2.update()

def write_video_buffer():
    while True:
        update_buffer()

        if stop_event.isSet():
            print("exiting")
            break
        if video_buffer.dirty:
            video_buffer.write()
        time.sleep(1.0 / FRAMERATE )


def strobe():
    print("strobe")
    white_mask()
    time.sleep(0.20)
    black_mask()

def meter_test():
    print("meter test")
    meter = PeakMeter() 

    level = 0
    A = .4
    t = 0  
    f = 0.195
    for t in range(30):
        val = A*math.sin(f*t) + .4
        meter.set(val)
        time.sleep(.020)

def osc():

    ip = "0.0.0.0"
    port = 37337

    def metronome(bpm, beat):
        print(bpm)
        scanner.metronome(bpm, beat)

    def color(args,r,g,b):
        background.red(r)
        background.green(g)
        background.blue(b)

    def envelope(args ):
        y,channel = args.split() 
        y = float(y)
        channel = int(channel)
        if channel == 1:
            peak_meter.set(float(y))
        elif channel == 2:
            peak_meter2.set(float(y))

    def default():
        print("default!")

    def fader_green(v):
        background.green(v)

    def fader_blue(v):
        background.blue(v)

    def fader_red(v):
        background.red(v)

    from pythonosc import dispatcher
    from pythonosc import osc_server

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/metronome", metronome)
    dispatcher.map("/color/sky", color)
    dispatcher.map("/audio/envelope", envelope)
    # dispatcher.map("/*", default)
    dispatcher.map("/1/fader1", fader_red)
    dispatcher.map("/1/fader2", fader_green)
    dispatcher.map("/1/fader3", fader_blue)

    server = osc_server.ThreadingOSCUDPServer((ip, port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()

def demo():
    meter_test()
    strobe()
    time.sleep(.5)
    blue_mask()
    time.sleep(.5)
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
        osc()
