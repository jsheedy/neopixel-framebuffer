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
        self.bpm = 120
        self.count = 1
        self.timestamp = datetime.now()

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

        if delta_beat > 1.05 or delta_beat < -0.05:
            delta_beat = np.clip(delta_beat, 0, 1)
            self.count = ((self.count) % 4) + 1
            self.timestamp = datetime.now()

        for scanner in self.scanners:
            n1,n2 = scanner['n1'], scanner['n2']
            r,g,b = scanner.get('color', (1,1,1))

            point = Point(self.pos, n2 - n1, width=scanner.get('width', 2))
            points = point.get_points()
            color_points = np.full((n2-n1)*3, fill_value=0, dtype=np.uint8)
            color_points[0::3] = r * points * 255
            color_points[1::3] = g * points * 255
            color_points[2::3] = b * points * 255
            self.video_buffer.merge(n1, n2, color_points)
