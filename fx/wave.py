import itertools

import numpy as np

from .fx import Fx

class ChannelArray():
    def __init__(self, N, phase, velocity):
        self.N = N
        self.buff = np.clip(np.sin(np.arange(N)*(8*np.pi/self.N)),0,1)
        self.phase = phase
        self.velocity = velocity
        self.intensity = 255

    def update(self, i):
        return (self.intensity * np.roll(self.buff, (self.phase+i*self.velocity)%self.N)) \
            .astype(np.uint8)

class Wave(Fx):

    def __init__(self, video_buffer, w=1):
        self.video_buffer = video_buffer
        self.N = self.video_buffer.N
        self.rgb_arrays = {
            'r': ChannelArray(self.N, 0, 1),
            'g': ChannelArray(self.N, 120, 2),
            'b': ChannelArray(self.N, 240, 3)
        }
        self.pointer = itertools.count(0)

    def update(self):
        super(Wave, self).update()
        if not self.enabled:
            return
        i = next(self.pointer)

        self.video_buffer.buffer[0:len(self.video_buffer.buffer):3] = self.rgb_arrays['r'].update(i)
        self.video_buffer.buffer[1:len(self.video_buffer.buffer):3] = self.rgb_arrays['g'].update(i)
        self.video_buffer.buffer[2:len(self.video_buffer.buffer):3] = self.rgb_arrays['b'].update(i)

