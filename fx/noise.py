import numpy as np

from .fx import Fx

class Noise(Fx):

    def __init__(self, video_buffer, **kwargs):
        super().__init__(video_buffer, **kwargs)

    def _update(self):
        self.video_buffer.buffer[:] = np.random.random_integers(0,255,self.video_buffer.N*3)
