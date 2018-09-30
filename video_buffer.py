from collections import OrderedDict
from datetime import datetime

import numpy as np


class VideoBuffer(object):
    frame = 0

    def __init__(self, N, resolution=None):
        if resolution is None:
            resolution = N

        self.buffer = np.zeros(shape=(resolution,3), dtype=np.float64)
        self.resolution = resolution
        self.N = N
        self.effects = OrderedDict()
        self.t0 = datetime.now()
        self.t = 0.0
        self.enabled = True
        self.device_x = np.linspace(0, 1, N)
        self.buffer_x = np.linspace(0, 1, resolution)

    def add_effect(self, name, fx, **kwargs):
        self.effects[name] = fx(self, **kwargs)


    def update(self):
        for key, effect in self.effects.items():
            if effect.enabled:
                effect.update()
        self.t = (datetime.now() - self.t0).total_seconds()
        self.frame += 1
        return self.frame

    def as_uint8(self):
        # interpolate from buffer resolution to device resolution
        r = np.interp(self.device_x, self.buffer_x, self.buffer[:,0]) * 255
        g = np.interp(self.device_x, self.buffer_x, self.buffer[:,1]) * 255
        b = np.interp(self.device_x, self.buffer_x, self.buffer[:,2]) * 255

        device_buffer = np.vstack((r,g,b)).T
        return device_buffer.astype(np.uint8).tobytes()