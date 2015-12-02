from collections import OrderedDict

import numpy as np


class VideoBuffer(object):
    frame = 0

    def __init__(self, N):
        self.buffer = np.zeros(N * 3, dtype=np.uint8)
        self.N = N
        self.effects = OrderedDict()

    def add_effect(self, name, fx, **kwargs):
        self.effects[name] = fx(self, **kwargs)

    def set(self, n, c):
        """ set pixel n to color c (r,g,b)"""
        self.buffer[n * 3:(n + 1) * 3] = c
        self.dirty = True

    def update(self):
        for key, effect in self.effects.items():
            if effect.enabled:
                effect.update()
        self.frame += 1
        return self.frame
