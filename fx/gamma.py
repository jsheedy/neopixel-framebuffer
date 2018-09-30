import colorsys

import numpy as np

from .fx import Fx


class Gamma(Fx):

    def __init__(self, video_buffer, gamma=2.4, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.set('', gamma)


    def set(self, addr, gamma):
        self.gamma = float(gamma)


    def _update(self):
        self.video_buffer.buffer = np.clip(self.video_buffer.buffer, 0, 1) ** self.gamma
