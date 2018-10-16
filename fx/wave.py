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
            'r': ChannelArray(self.x[:,0], video_buffer, wavelength=3, freq=-2),
            'g': ChannelArray(self.x[:,1], video_buffer, wavelength=2, freq=1),
            'b': ChannelArray(self.x[:,2], video_buffer, wavelength=.5, freq=3),
        }

    def _update(self):

        self.hue += self.hue_speed
        # r,g,b = colorsys.hsv_to_rgb(self.hue % 1, 1, 1)

        r_a = self.rgb_arrays['r'].update()
        g_a = self.rgb_arrays['g'].update()
        b_a = self.rgb_arrays['b'].update()

        rr = .8
        rg = .1
        rb = .1

        gr = .1
        gg = .9
        gb = .0

        br = .3
        bg = .3
        bb = .4

        self.x[:,0] = rr * r_a + rg * g_a  + rb * b_a
        self.x[:,1] = gr * r_a + gg * g_a +  gb * b_a
        self.x[:,2] = br * r_a + bg * g_a +  bb * b_a

        return self.x
