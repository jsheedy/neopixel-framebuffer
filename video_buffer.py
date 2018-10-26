from collections import OrderedDict
from datetime import datetime
from functools import reduce
import operator

import numpy as np


operator_map = {
    'add': operator.add,
    'subtract': operator.sub,
    'multiply': operator.mul,
    'divide': operator.truediv,
    'power': operator.pow
}

class VideoBuffer(object):
    frame = 0


    def __init__(self, N, resolution=None, operator=operator.add):
        if resolution is None:
            resolution = N

        self.buffer = np.zeros(shape=(resolution,3), dtype=np.float64)
        self.resolution = resolution
        self.N = N
        self.effects = OrderedDict()
        self.t0 = datetime.now()
        self.t = 0.0
        self.delta_time = 0.0
        self.enabled = True
        self.device_x = np.linspace(0, 1, N)
        self.buffer_x = np.linspace(0, 1, resolution)
        self.gamma = 2.4
        self.brightness = 1.0
        self.operator = operator
        self.uint8 = self.as_uint8()


    def add_effect(self, name, fx, **kwargs):
        self.effects[name] = fx(self, **kwargs)


    def set_gamma(self, addr, gamma):
        self.gamma = float(gamma)


    def set_brightness(self, addr, brightness):
        self.brightness = float(brightness)


    def set_operator(self, addr, on):

        if on == 1.0:
            op = addr.split('/')[-1]
            self.operator = op


    def update(self):
        layers = []
        for _key, effect in self.effects.items():
            if effect.enabled and (not effect.is_post_process):
                layer = effect.update()
                if layer is not None:
                    layers.append(layer)

        if layers:
            op = operator_map[self.operator]
            self.buffer += reduce(op, layers)

        # brightness
        self.buffer -= (1.0-self.brightness)

        for _key, effect in self.effects.items():
            if effect.enabled and effect.is_post_process:
                self.buffer = effect.update()

        self.uint8 = self.as_uint8()
        t = (datetime.now() - self.t0).total_seconds()
        self.delta_time = t - self.t
        self.t = t
        self.frame += 1
        return self.frame


    def as_uint8(self):

        # gamma correction
        buff = np.clip(self.buffer, 0, 1) ** self.gamma

        # interpolate from buffer resolution to device resolution
        r = np.interp(self.device_x, self.buffer_x, buff[:,0]) * 255
        g = np.interp(self.device_x, self.buffer_x, buff[:,1]) * 255
        b = np.interp(self.device_x, self.buffer_x, buff[:,2]) * 255

        device_buffer = np.vstack((r,g,b)).T
        return device_buffer.astype(np.uint8).tobytes()