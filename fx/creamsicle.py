import colorsys

import numpy as np

from .fx import Fx


class Creamsicle(Fx):

    def __init__(self, video_buffer, level=1.0, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.level = level
        self.w = 8 * 2*np.pi / self.N
        self.x = self.w * self.x[:,0]

        h = 30 / 360
        v = 1
        _rgb = [colorsys.hsv_to_rgb(h,s/(2**16-1),v) for s in range(2**16)]
        self.rgb = np.array(_rgb)


    def _update(self):
        phase = self.video_buffer.t * 2
        wave = ((np.sin(self.x + phase) / 2 + 0.5)*(2**16-1)).astype(np.uint16)
        colors = self.rgb[wave]
        return colors