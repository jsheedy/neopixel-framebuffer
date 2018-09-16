import colorsys

import numpy as np

from .fx import Fx


class Creamsicle(Fx):

    def __init__(self, video_buffer, level=1.0, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.level = level
        self.w = 8 * 2*np.pi / self.N
        self.x = self.w * self.x
        h = 30 / 360
        v = 1
        self.rgb = []
        for s in range(256):
            rgb = colorsys.hsv_to_rgb(h,s/255,v)
            self.rgb.append([self.gamma[int(255*x)] for x in rgb])


    def _update(self):
        phase = self.video_buffer.t * 2
        y = (255 * (np.sin(self.x + phase) / 2 + 0.5)).astype(np.uint8)
        rgb_tuples = [self.rgb[s] for s in y]
        # flatten list of lists
        rgb = [rgb for sublist in rgb_tuples for rgb in sublist]
        self.video_buffer.buffer[:] = rgb
