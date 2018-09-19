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
        self.buffer = np.full(self.video_buffer.N*3, fill_value=0, dtype=np.float64)

        self.rgb_arrays = {
            'r': ChannelArray(self.x, video_buffer, wavelength=10, freq=2),
            'g': ChannelArray(self.x, video_buffer, wavelength=20, freq=1),
            'b': ChannelArray(self.x, video_buffer, wavelength=30, freq=2),
            's': ChannelArray(self.x, video_buffer, wavelength=40, freq=2),
            'v': ChannelArray(self.x, video_buffer, wavelength=50, freq=2)
        }

    def _update(self):

        self.hue += self.hue_speed
        r, g, b = colorsys.hsv_to_rgb(self.hue % 1, 1, 1)

        self.buffer[::3] = self.gamma_norm(r) * self.rgb_arrays['r'].update()
        self.buffer[1::3] = self.gamma_norm(g) * self.rgb_arrays['g'].update()
        self.buffer[2::3] = self.gamma_norm(b) * self.rgb_arrays['b'].update()

        self.video_buffer.merge(self.buffer)
