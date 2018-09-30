import numpy as np

from .fx import Fx

class FadeBackGround(Fx):

    def __init__(self, video_buffer, q=.01, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.q = q

    def _update(self):
        self.video_buffer.buffer -= self.q