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
        if random.random() > .95:
            self.freq += 0.001*(random.random() - .5)
        return np.sin(self.x + phase) * self.brightness

class Wave(Fx):

    freqs = list(range(-5, 5))
    wavelengths = list(range(1, 20))

    def __init__(self, video_buffer, w=1, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.N = self.video_buffer.N
        self.buffer = np.full(self.video_buffer.N*3, fill_value=0)

        self.rgb_arrays = {
            'r': ChannelArray(self.N, wavelength=10, brightness=random.randrange(200,256), freq=.510),
            # 'r': ChannelArray(self.N, wavelength=random.choice(self.wavelengths), brightness=random.randrange(200,256), freq=random.choice(self.freqs)),
            'g': ChannelArray(self.N, wavelength=20, brightness=random.randrange(200,256), freq=.2),
            'b': ChannelArray(self.N, wavelength=30, brightness=random.randrange(200,256), freq=-.4)
        }

    def _update(self):

        self.buffer[::3] = self.rgb_arrays['r'].update()
        self.buffer[1::3] = self.rgb_arrays['g'].update()
        self.buffer[2::3] = self.rgb_arrays['b'].update()

        self.video_buffer.merge(0, self.video_buffer.N, self.buffer)

