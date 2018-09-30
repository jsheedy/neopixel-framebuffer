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
        # _rgb = []
        # for s in range(256):
        #     rgb = colorsys.hsv_to_rgb(h,s/255,v)
        #     _rgb.append([int(255*c) for c in rgb])

        # self.rgb = np.array(_rgb, dtype=np.uint8)


    def _update(self):
        phase = self.video_buffer.t * 2
        self.video_buffer += np.sin(self.x + phase) / 2 + 0.5
