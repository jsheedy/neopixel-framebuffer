from collections import OrderedDict

import numpy as np


class VideoBuffer(object):
    frame = 0

    def __init__(self, N):
        self.buffer = np.zeros(N * 3, dtype=np.uint8)
        self.N = N
        self.effects = OrderedDict()
        self.locked = False

    def add_effect(self, name, fx, **kwargs):
        self.effects[name] = fx(self, **kwargs)

    def set(self, n, c):
        """ set pixel n to color c (r,g,b)"""
        self.buffer[n * 3:(n + 1) * 3] = c
        self.dirty = True

    def merge(self, n1, n2, array, clip=True):
        """ merge array into the video_buffer between points
        n1 and n2, handling clipping """

        array = array.astype(np.uint32)
        slice = self.buffer[n1*3:n2*3]
        int32_slice = slice.astype(np.int32)
        int32_slice[:] += array[:]
        int32_uint8_slice = np.clip(int32_slice,0,255).astype(np.uint8)
        self.buffer[n1*3:n2*3] = int32_uint8_slice

    def update(self):
        for key, effect in self.effects.items():
            if effect.enabled:
                effect.update()
        self.frame += 1
        return self.frame
