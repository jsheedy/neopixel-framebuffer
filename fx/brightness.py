import numpy as np

from .fx import Fx


class Brightness(Fx):

    def __init__(self, video_buffer, level=1.0, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.level = level


    def set(self, addr, value):
        self.level = value


    def _update(self):
        self.video_buffer.buffer = np.multiply(self.video_buffer.buffer, self.level).astype(np.uint8)

        # in-place range bounded addition with numexpr. Faster or slower?
        # https://stackoverflow.com/questions/29611185/avoid-overflow-when-adding-numpy-arrays
        # import numexpr
        # numexpr.evaluate('where((a+b)>255, 255, a+b)', out=a, casting='unsafe')