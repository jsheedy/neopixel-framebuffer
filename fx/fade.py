import logging

import numpy as np

from .fx import Fx

class FadeBackGround(Fx):

    def __init__(self, video_buffer, q=.5, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.q = q


    def set(self, _addr, q):
        self.q = q


    def _update(self):
        dq = self.q / 10
        self.video_buffer.buffer[self.video_buffer.buffer >= dq] -= dq
