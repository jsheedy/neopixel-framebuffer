from datetime import datetime
import itertools
import random

import numpy as np

from .fx import Fx

class ChannelArray():
    def __init__(self, N, wavelength=8, brightness=255, freq=1):
        self.N = N
        self.wavelength = wavelength
        self.freq = freq
        self.brightness = brightness
        self.timestamp = datetime.now()
        self.x = np.arange(self.N)*(self.wavelength*np.pi/self.N)

    def update(self):
        new_timestamp = datetime.now()
        delta_t = (new_timestamp - self.timestamp).total_seconds()
        phase = delta_t / self.freq
        return np.sin(self.x + phase) * self.brightness

class Wave(Fx):

    freqs = (-3,-2,-1,1,2,3)

    def __init__(self, video_buffer, w=1, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.N = self.video_buffer.N
        self.buffer = np.full(self.video_buffer.N*3, fill_value=0)

        self.rgb_arrays = {
            'r': ChannelArray(self.N, wavelength=4, brightness=random.randrange(200,256), freq=random.choice(self.freqs)),
            'g': ChannelArray(self.N, wavelength=8, brightness=random.randrange(200,256), freq=random.choice(self.freqs)),
            'b': ChannelArray(self.N, wavelength=12, brightness=random.randrange(200,256), freq=random.choice(self.freqs))
        }

    def _update(self):

        self.buffer[::3] = self.rgb_arrays['r'].update()
        self.buffer[1::3] = self.rgb_arrays['g'].update()
        self.buffer[2::3] = self.rgb_arrays['b'].update()

        self.video_buffer.merge(0, self.video_buffer.N, self.buffer)

