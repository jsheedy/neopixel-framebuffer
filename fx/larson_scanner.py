from datetime import datetime, timedelta
import logging

import numpy as np
import numexpr

from .fx import Fx
from point import Point


class LarsonScanner(Fx):
    def __init__(self, video_buffer, scanners, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.scanners = scanners
        self.pos = 0.0
        self.bpm = 120
        self.count = 1
        self.timestamp = datetime(2000,1,1)

    def metronome(self, endpoint, bpm, count):
        logging.info("scanner setting bpm: {}".format(bpm))
        self.timestamp = datetime.now()
        self.bpm = int(bpm)
        self.count = int(count)

    def update(self):
        super(LarsonScanner, self).update()

        N = self.video_buffer.N
        secs = (datetime.now() - self.timestamp).total_seconds()

        # if we haven't seen a metronome() call in 2 seconds, revert to autoscan
        delta_beat = secs / (60.0/self.bpm)

        if self.count in (1,3):
            self.pos = delta_beat
        else:
            self.pos =  1-delta_beat

        if delta_beat > 1.05 or delta_beat < -0.05:
            delta_beat = np.clip(delta_beat, 0, 1)
            self.count = ((self.count) % 4) + 1
            self.timestamp = datetime.now()

        for scanner in self.scanners:

            n1,n2 = scanner['n1'], scanner['n2']
            point = Point(self.pos, n2 - n1, width=scanner.get('width', 2))
            points = point.get_points()

            slice = self.video_buffer.buffer[n1*3:n2*3]
            int32_slice = slice.astype(np.int32)
            r,g,b = scanner.get('color', (1,1,1))
            int32_slice[0::3] += (r*points.astype(np.uint32)).astype(np.uint32)
            int32_slice[1::3] += (g*points.astype(np.uint32)).astype(np.uint32)
            int32_slice[2::3] += (b*points.astype(np.uint32)).astype(np.uint32)

            int32_uint8_slice=np.clip(int32_slice,0,255).astype(np.uint8)
            # numexpr.evaluate('where((slice+int32_uint8_slice)>255, 255, slice+int32_uint8_slice)', out=slice, casting='unsafe')
            self.video_buffer.buffer[n1*3:n2*3] = int32_uint8_slice

