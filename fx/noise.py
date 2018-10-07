import numpy as np

from .fx import Fx

class Noise(Fx):

    def _update(self):
        self.video_buffer.buffer += np.random.random_sample(size=(self.N,3))
