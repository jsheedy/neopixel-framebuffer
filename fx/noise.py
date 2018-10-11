import numpy as np

from .fx import Fx

class Noise(Fx):

    def _update(self):
        return np.random.random_sample(size=(self.N,3))
