import colorsys

import numpy as np

from .fx import Fx


class BackGround(Fx):

    def __init__(self, video_buffer, color=None, intensity=1.0, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.intensity = intensity
        self.N = self.video_buffer.N
        color = color or (1,0,0)
        self.parameters = {'r': color[0], 'g': color[1], 'b': color[2]}


    def set(self, addr, value, color='r'):
        self.parameters[color] = value


    def _update(self):
        p = self.parameters
        r,g,b = p['r'], p['g'], p['b']
        self.video_buffer.buffer[:, 0] = self.intensity*r
        self.video_buffer.buffer[:, 1] = self.intensity*g
        self.video_buffer.buffer[:, 2] = self.intensity*b
