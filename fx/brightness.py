import numpy as np

from .fx import Fx


class Brightness(Fx):

    def __init__(self, video_buffer, level=1.0, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.level = level

    def _update(self):
        self.video_buffer.buffer = np.multiply(self.video_buffer.buffer, self.level).astype(np.uint8)
