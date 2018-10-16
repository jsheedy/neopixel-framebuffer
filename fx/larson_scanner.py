from datetime import datetime
import logging

import numpy as np

from .fx import Fx
from point import Point


class LarsonScanner(Fx):
    def __init__(self, video_buffer, scanners, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.scanners = scanners
        self.pos = 0.0
        self.bpm = 60
        self.count = 1
        self.timestamp = datetime.now()
        self.color_points = np.zeros(shape=(self.N,3))


    def metronome(self, _, bpm, count):
        logging.debug("scanner setting bpm: {}".format(bpm))
        self.timestamp = datetime.now()
        self.bpm = int(bpm)
        self.count = int(count)


    def _update(self):
        secs = (datetime.now() - self.timestamp).total_seconds()
        # if we haven't seen a metronome() call in 2 seconds, revert to autoscan
        delta_beat = secs / (60.0/self.bpm)

        if self.count in (1, 3):
            self.pos = delta_beat
        else:
            self.pos =  1 - delta_beat

        if delta_beat > 1.00 or delta_beat < 0.0:
            delta_beat = np.clip(delta_beat, 0, 1)
            self.count = ((self.count) % 4) + 1
            self.timestamp = datetime.now()

        self.color_points[:] = 0
        for scanner in self.scanners:
            p1,p2 = scanner['p1'], scanner['p2']
            r,g,b = scanner.get('color', (1,1,1))
            pos = p1 + self.pos*(p2-p1)
            point = Point(pos, self.N, width=scanner.get('width',0.01))
            points = point.get_points()

            self.color_points[:,0] += r * points
            self.color_points[:,1] += g * points
            self.color_points[:,2] += b * points

        return self.color_points
