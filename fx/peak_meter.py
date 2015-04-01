from .fx import Fx
from point import Point

import numpy as np

import random

class Meter():
    def __init__(self, n1=0, n2=100, reverse=False):
        self.set(0)
        self.n1 = n1
        self.n2 = n2
        self.level = 0.0
        self.N = self.n2 - self.n1
        self.buff = np.zeros(self.N*3)

    def set(self, level):
        """level 0 -> 1"""
        self.level = level

    def get_points(self):
        self.buff *= .7
        self.buff[1:self.N*3-1:3] = self.buff[0:self.N*3:3]*.2
        self.buff[2:self.N*3-6:3] = self.buff[0:self.N*3-6:3]*.3
        # self.buff = np.roll(self.buff,1)
        pos = int(self.level * self.N)
        self.buff[0:pos*3:3] = [255]*pos
        if not pos == self.N:
            self.buff[0+pos*3] = 255*((self.level*self.N)-pos)
        return self.buff

class PeakMeter(Fx):
    def __init__(self, video_buffer, meters):
        self.video_buffer = video_buffer
        self.meters = []
        for d in meters:
            print(d)
            self.meters.append(Meter(**d))

    def envelope(self, name, y, channel ):
        y = float(y)
        channel = int(channel)
        self.meters[channel-1].set(float(y))

    def update(self):
        super(PeakMeter, self).update()
        if not self.enabled:
            return

        for meter in self.meters:
            self.video_buffer.buffer[meter.n1*3:meter.n2*3] = meter.get_points()