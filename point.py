import functools
import math

import numpy as np

def gaussian(x, a=1, b=1, c=2):
    y = a * math.exp(- ((x-b)**2) / (2*c**2) )
    return y

class Point():
    """ represent a point as a gaussian distribution that can
    be placed anywhere on the line of N units.  position is
    in the normalized range (0.0, 1.0)
    """

    def __init__(self, pos, N, width=1.5):
        """ pos is in range (0,1) """
        self.N = N
        self.pos = pos
        self.width = width

    def get_points(self, margin=0.2):
        """returns numpy array of N points"""
        relativePos = margin*self.N + self.pos * ((1-margin)*self.N)
        f = functools.partial(gaussian, a=255, b=relativePos, c=self.width)
        points = np.array(list(map(f, range(self.N))))
        return points
