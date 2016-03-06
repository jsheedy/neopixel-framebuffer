import numpy as np

from .fx import Fx

class FadeBackGround(Fx):

    def __init__(self, video_buffer, q=1):
        super().__init__(video_buffer)
        self.q = q

    def _update(self):
        self.video_buffer.buffer[self.video_buffer.buffer >= self.q] -= self.q
        self.video_buffer.buffer[self.video_buffer.buffer < self.q] = 0