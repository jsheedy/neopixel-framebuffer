from datetime import datetime
import logging
import random

import numpy as np

from .fx import Fx
from point import Point


class Meter():
    def __init__(self, n1=0, n2=100, reverse=False, color=(1,1,1)):
        self.set(0)
        self.n1 = n1
        self.n2 = n2
        self.level = 0.0
        self.N = self.n2 - self.n1
        self.buff = np.zeros(self.N*3, dtype=np.float)
        self.reverse = reverse
        self.color = color
        self.timestamp = datetime(2000,1,1)

    def set(self, level):
        """level 0 -> 1"""
        self.level = np.clip(level, 0, 1)
        self.timestamp = datetime.now()

    def get_points(self):
        self.buff[:] = 0
        pos = int(self.level * self.N)
        r,g,b = self.color
        array = np.full(pos, fill_value=255, dtype=np.uint32)
        if self.reverse:
            if not pos == self.N:
                self.buff[3*(self.N-pos)+0:(self.N+0)*3:3] = array*r
                self.buff[3*(self.N-pos)+1:(self.N+1)*3:3] = array*g
                self.buff[3*(self.N-pos)+2:(self.N+2)*3:3] = array*b
        else:
            self.buff[0:pos*3:3] = array*r
            self.buff[1:pos*3:3] = array*g
            self.buff[2:pos*3:3] = array*b
        return self.buff

class PeakMeter(Fx):
    def __init__(self, video_buffer, meters, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.meters = [Meter(**d) for d in meters]


    def envelope(self, name, y, channel ):
        y = float(y)
        channel = int(channel)
        self.meters[channel-1].set(float(y))

    def _update(self):

        for meter in self.meters:
            secs = (datetime.now() - meter.timestamp).total_seconds()
            if secs > 2:
                continue
            color_points = meter.get_points()
            self.video_buffer.merge(meter.n1, meter.n2, color_points)
