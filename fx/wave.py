import itertools
import random

import numpy as np

from .fx import Fx

class ChannelArray():
    def __init__(self, N, wavelength=8, velocity=1):
        self.N = N
        self.buff = np.clip(np.sin(np.arange(N)*(wavelength*np.pi/self.N)),0,1)
        self.velocity = velocity
        self.wavelength = wavelength
        self.intensity = 255

    def update(self, i):
        # if random.random() > .97:
        #     self.velocity += 1-random.randint(0,2)
        #     if self.velocity > 4:
        #         self.velocity -= 1
        #     elif self.velocity < -4:
        #         self.velocity += 1
        if random.random() > .99:
            self.velocity *= -1
            # self.velocity += (random.random() - 0.5)

        return (self.intensity * np.roll(self.buff, (i*self.velocity)%self.N)) \
            .astype(np.uint8)

class Wave(Fx):

    def __init__(self, video_buffer, w=1):
        self.video_buffer = video_buffer
        self.N = self.video_buffer.N
        self.rgb_arrays = {
            'r': ChannelArray(self.N, wavelength=4, velocity=1),
            'g': ChannelArray(self.N, wavelength=8, velocity=2),
            'b': ChannelArray(self.N, wavelength=12, velocity=2)
        }
        self.pointer = itertools.count(0)

    def update(self):
        super(Wave, self).update()

        i = next(self.pointer)

        self.video_buffer.buffer[::3] = self.rgb_arrays['r'].update(i)
        self.video_buffer.buffer[1::3] = self.rgb_arrays['g'].update(i)
        self.video_buffer.buffer[2::3] = self.rgb_arrays['b'].update(i)

