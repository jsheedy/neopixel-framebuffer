from datetime import datetime
import logging

import numpy as np

from .fx import Fx
from point import Point


class LarsonScanner(Fx):
    def __init__(self, video_buffer, scanners):
        self.video_buffer = video_buffer
        self.scanners = scanners
        self.pos = 0.0
        self.bpm = 120
        self.count = 1
        self.timestamp = datetime(2000,1,1)
        self.velocity = .04
        self.delta_beat = 2.0

    def metronome(self, endpoint, bpm, count):
        logging.info("scanner setting bpm: {}".format(bpm))
        self.timestamp = datetime.now()
        self.bpm = int(bpm)
        self.count = int(count)

    def update(self):
        super(LarsonScanner, self).update()
        if not self.enabled:
            return

        N = self.video_buffer.N

        secs = (datetime.now() - self.timestamp).total_seconds()

        # if we haven't seen a metronome() call in 2 seconds,
        # revert to autoscan
        if self.delta_beat > 1.1 or self.delta_beat < -.1 or secs > 4:
            self.delta_beat = 0
            self.pos += self.velocity
            if self.pos > 1:
                self.pos = 1
                self.velocity *= -1
            elif self.pos < 0:
                self.pos = 0
                self.velocity *= -1

        else:
            self.delta_beat = secs / (60.0/self.bpm)
            self.velocity = (self.bpm/60.0)/26
            if self.count in (1,3):
                self.pos = self.delta_beat
            else:
                self.pos =  1-self.delta_beat

        for scanner in self.scanners:

            n1,n2 = scanner['n1'], scanner['n2']
            point = Point(self.pos, n2 - n1, width=5)
            points = point.get_points()

            slice = self.video_buffer.buffer[0+n1*3:n2*3:3].astype(np.int32)
            slice += points
            slice.clip(0,255,out=slice)
            self.video_buffer.buffer[0+n1*3:n2*3:3] = slice
            # self.video_buffer.buffer[0+n1*3:n2*3:3] += points
            # self.video_buffer.buffer[2+n1*3:n2*3:3] *= .1 # bring down other fx first
            # self.video_buffer.buffer[2+n1*3:n2*3:3] += points*.4