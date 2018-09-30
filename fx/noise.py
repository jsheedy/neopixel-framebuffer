import numpy as np

from .fx import Fx

class Noise(Fx):

    def __init__(self, video_buffer, **kwargs):
        super().__init__(video_buffer, **kwargs)

    def _update(self):
        self.video_buffer.merge(np.random.random_sample(size=self.video_buffer.N*3))
