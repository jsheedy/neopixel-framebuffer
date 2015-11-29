import numpy as np

from .fx import Fx

class FadeBackGround(Fx):

    def __init__(self, video_buffer, q=1):
        self.video_buffer = video_buffer
        self.q = q

    def update(self):
        self.video_buffer.buffer[self.video_buffer.buffer >= self.q] -= self.q
        self.video_buffer.buffer[self.video_buffer.buffer < self.q] = 0