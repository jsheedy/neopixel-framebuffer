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

    def update(self):
        new_timestamp = datetime.now()
        delta_t = (new_timestamp - self.timestamp).total_seconds()

        phase = delta_t / self.freq
        x = np.arange(self.N)
        wave = np.sin(x*(self.wavelength*np.pi/self.N) + phase) * self.brightness

        return np.clip(wave, 0, 255).astype(np.uint8)

class Wave(Fx):

    freqs = (-3,-2,-1,1,2,3)

    def __init__(self, video_buffer, w=1, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.N = self.video_buffer.N


        self.rgb_arrays = {
            'r': ChannelArray(self.N, wavelength=4, brightness=random.randrange(0,256), freq=random.choice(self.freqs)),
            'g': ChannelArray(self.N, wavelength=8, brightness=random.randrange(0,256), freq=random.choice(self.freqs)),
            'b': ChannelArray(self.N, wavelength=12, brightness=random.randrange(0,256), freq=random.choice(self.freqs))
        }

    def update(self):
        super(Wave, self).update()

        self.video_buffer.buffer[::3] = self.rgb_arrays['r'].update()
        self.video_buffer.buffer[1::3] = self.rgb_arrays['g'].update()
        self.video_buffer.buffer[2::3] = self.rgb_arrays['b'].update()
