import numpy as np

from .fx import Fx


class Brightness(Fx):

    def __init__(self, video_buffer, level=1.0, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.level = level


    def set(self, addr, value):
        self.level = value


    def _update(self):
        self.video_buffer.buffer -= (1.0-self.level)
