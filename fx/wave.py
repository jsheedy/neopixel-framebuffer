from datetime import datetime
import itertools
import random

import numpy as np

from .fx import Fx

class ChannelArray():
    def __init__(self, N, wavelength=8, freq=1):
        self.N = N
        self.wavelength = wavelength
        self.freq = freq
        self.forward = True
        self.timestamp = datetime.now()

    def update(self):
        # if random.random() > .999:
        #     self.forward = not self.forward

        new_timestamp = datetime.now()
        delta_t = (new_timestamp - self.timestamp).total_seconds()

        phase = delta_t / self.freq

        if self.forward:
            x = np.arange(self.N)
        else:
            x = np.arange(self.N-1,-1,-1)

        wave = np.sin(x*(self.wavelength*np.pi/self.N) + phase)*255

        return np.clip(wave, 0, 255).astype(np.uint8)

class Wave(Fx):

    def __init__(self, video_buffer, w=1, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.N = self.video_buffer.N

        self.rgb_arrays = {
            'r': ChannelArray(self.N, wavelength=4, freq=1),
            'g': ChannelArray(self.N, wavelength=8, freq=2),
            'b': ChannelArray(self.N, wavelength=12, freq=2)
        }

    def update(self):
        super(Wave, self).update()

        self.video_buffer.buffer[::3] = self.rgb_arrays['r'].update()
        self.video_buffer.buffer[1::3] = self.rgb_arrays['g'].update()
        self.video_buffer.buffer[2::3] = self.rgb_arrays['b'].update()
