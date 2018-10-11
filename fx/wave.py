import colorsys
from datetime import datetime
import itertools
import random

import numpy as np

from .fx import Fx


class ChannelArray():
    def __init__(self, x, video_buffer, wavelength=8, brightness=255, freq=1):
        self.wavelength = wavelength
        self.freq = freq
        self.brightness = brightness
        w = self.wavelength * 2 * np.pi / len(x)
        self.x = w * x
        self.video_buffer = video_buffer

    def update(self):
        phase = self.video_buffer.t * self.freq
        if random.random() > .95:
            self.freq += np.clip(0.001*(random.random() - .5), -5, 5)
        return np.sin(self.x + phase) / 2 + 0.5


class Wave(Fx):

    freqs = list(range(-5, 5))
    wavelengths = list(range(1, 20))
    hue_speed = .005
    hue = 0

    def __init__(self, video_buffer, w=1, **kwargs):
        super().__init__(video_buffer, **kwargs)

        self.rgb_arrays = {
            'r': ChannelArray(self.x[:,0], video_buffer, wavelength=10, freq=2),
            'g': ChannelArray(self.x[:,1], video_buffer, wavelength=20, freq=1),
            'b': ChannelArray(self.x[:,2], video_buffer, wavelength=30, freq=2),
        }

    def _update(self):

        self.hue += self.hue_speed
        r,g,b = colorsys.hsv_to_rgb(self.hue % 1, 1, 1)

        self.x[:,0] = r * self.rgb_arrays['r'].update()
        self.x[:,1] = g * self.rgb_arrays['g'].update()
        self.x[:,2] = b * self.rgb_arrays['b'].update()

        return self.x
