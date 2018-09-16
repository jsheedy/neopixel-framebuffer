import colorsys

import numpy as np

from .fx import Fx


class BackGround(Fx):

    def __init__(self, video_buffer, color=None, intensity=1.0, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.intensity = intensity
        self.N = self.video_buffer.N
        color = color or [255, 0, 0]
        self.parameters = {'r': color[0], 'g': color[1], 'b': color[2]}

    def set(self, addr, cc, value, channel):
        if cc == 22:  # K1 knob
            self.parameters['r'] = value * 2
        elif cc == 23:  # K2 knob
            self.parameters['r'] = value * 2
        elif cc == 24:  # K3 knob
            self.parameters['r'] = value * 2
        elif cc == 25:  # K4 knob
            self.intensity = value / 127
        elif cc == 34:  # breath
            h = value / 127
            s = 1.0
            v = 1.0
            # self.intensity = value / 127  # np.clip(value, 0, 1)
            self.parameters['r'],self.parameters['g'],self.parameters['b'] = list(map(lambda x: x*255, colorsys.hsv_to_rgb(h,s,v)))
            self.parameters['r'] = value * 2

    def clear(self, x):
        self.video_buffer.buffer[:] = 0

    def _update(self):
        p = self.parameters
        r,g,b = p['r'], p['g'], p['b']
        self.video_buffer.buffer[0:self.N*3:3] = int(self.intensity*r)
        self.video_buffer.buffer[1:self.N*3:3] = int(self.intensity*g)
        self.video_buffer.buffer[2:self.N*3:3] = int(self.intensity*b)