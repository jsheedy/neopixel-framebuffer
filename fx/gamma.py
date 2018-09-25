import colorsys

import numpy as np

from .fx import Fx


class Gamma(Fx):

    def __init__(self, video_buffer, gamma=2.4, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.set('', gamma)


    def set(self, addr, gamma):
        self.gamma =(255*(np.arange(256,dtype=np.float64)/255) ** gamma).astype(np.uint8)


    def _update(self):

        self.video_buffer.buffer[:] = self.gamma[self.video_buffer.buffer]
