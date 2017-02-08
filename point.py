import numpy as np


class Point():
    """ represent a point as a gaussian distribution that can
    be placed anywhere on the line of N units.  position is
    in the normalized range (0.0, 1.0)
    """

    def __init__(self, pos, N, width=1.0):
        """ pos is in range (0,1) """
        self.N = N
        self.pos = pos
        self.width = width
        self.hat = (0,1.0,0)

    def get_points(self):
        """returns numpy array of N points"""
        relativePos = self.width + self.pos * (self.N - 2*self.width)
        return np.interp(range(self.N), (relativePos - self.width,relativePos, relativePos + self.width), self.hat)
