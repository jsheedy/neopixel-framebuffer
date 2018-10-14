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
        return np.sin(self.x + phase) / 2 + 0.5


class Wave(Fx):

    hue_speed = .005
    hue = 0

    def __init__(self, video_buffer, w=1, **kwargs):
        super().__init__(video_buffer, **kwargs)

        self.rgb_arrays = {
            'r': ChannelArray(self.x[:,0], video_buffer, wavelength=10, freq=-2),
            'g': ChannelArray(self.x[:,1], video_buffer, wavelength=20, freq=1),
            'b': ChannelArray(self.x[:,2], video_buffer, wavelength=30, freq=3),
        }

    def _update(self):

        self.hue += self.hue_speed
        # r,g,b = colorsys.hsv_to_rgb(self.hue % 1, 1, 1)
        r = g = b = 1

        r_a = self.rgb_arrays['r'].update()
        g_a = self.rgb_arrays['g'].update()
        b_a = self.rgb_arrays['b'].update()

        self.x[:,0] = r * r_a * g_a
        self.x[:,1] = g * g_a * b_a
        self.x[:,2] = b * b_a * r_a

        return self.x
