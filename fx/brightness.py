import numpy as np

from .fx import Fx

class Brightness(Fx):

    def __init__(self, video_buffer, level=0.01):
        super().__init__(video_buffer)
        self.level = level

    def _update(self):
        self.video_buffer.buffer = np.multiply(self.video_buffer.buffer, self.level).astype(np.uint8)
