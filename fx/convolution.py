import colorsys
import itertools
from datetime import datetime

import numpy as np
import random

from .fx import Fx

class Convolution(Fx):

    ramp = itertools.cycle(np.arange(0,1,.005))

    def __init__(self, video_buffer, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.kernel = np.array([1/3, 1/3, 1/3])
        self.t0 = datetime.timestamp(datetime.now())

    def _update(self):

        r_convolution = np.convolve(self.video_buffer.buffer[0:3*self.video_buffer.N:3], self.kernel)
        g_convolution = np.convolve(self.video_buffer.buffer[1:3*self.video_buffer.N:3], self.kernel)
        b_convolution = np.convolve(self.video_buffer.buffer[2:3*self.video_buffer.N:3], self.kernel)

        self.video_buffer.buffer[0:3*self.video_buffer.N:3] = r_convolution[1:-1]
        self.video_buffer.buffer[1:3*self.video_buffer.N:3] = g_convolution[1:-1]
        self.video_buffer.buffer[2:3*self.video_buffer.N:3] = b_convolution[1:-1]

        # add glitch to taste
        rval = next(self.ramp)
        if random.random() >  rval:
            return
        # birth new pulse
        h = ((datetime.timestamp(datetime.now()) - self.t0) % 100) / 100
        s = random.random()
        v = random.random()
        idx = random.randint(0, self.video_buffer.N-1)
        rgb = tuple(map(lambda x: x*255, colorsys.hsv_to_rgb(h, s, v)))
        self.video_buffer.buffer[idx*3:idx*3+3] = rgb
