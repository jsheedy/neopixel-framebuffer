import itertools

import numpy as np

class Wave(object):

    def __init__(self, video_buffer, w=2):
        self.video_buffer = video_buffer
        self.N = self.video_buffer.N
        self.w=w
        self.pointer = itertools.count(0)

    def update(self):
        i = next(self.pointer)
        rbuff = ((np.sin(self.w*np.arange(self.N)*2*np.pi/self.N + i/10.0) + 1) * 127 ).astype(np.uint8)
        self.video_buffer.buffer[0:len(self.video_buffer.buffer):3] = rbuff

        bbuff = ((np.sin(1.05*self.w*np.arange(self.N)*2*np.pi/self.N + i/9.0) + 1) * 127 ).astype(np.uint8)
        self.video_buffer.buffer[2:len(self.video_buffer.buffer):3] = bbuff

        gbuff = ((np.sin(.95*self.w*np.arange(self.N)*2*np.pi/self.N + i/11.0) + 1) * 127 ).astype(np.uint8)
        self.video_buffer.buffer[1:len(self.video_buffer.buffer):3] = gbuff

        self.video_buffer.dirty = True
