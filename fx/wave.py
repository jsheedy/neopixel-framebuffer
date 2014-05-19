import itertools

import numpy as np

class Wave(object):

    def __init__(self, video_buffer, w=1):
        self.video_buffer = video_buffer
        self.N = self.video_buffer.N
        self.array = np.arange(self.N)
        self.w=w
        self.pointer = itertools.count(0)

    def triangle(self, i):
        """convert int 0->255 to 0->255->0 triangle wave"""
        if i > 127:
            return abs(128-((i-128)%128))
        else:
            return i
        
    def update(self):
        i = next(self.pointer)

        r_intensity = self.triangle(i%256)
        r_intensity = 255
        r_phase = 0
        g_intensity = self.triangle((i+80)%256)
        g_phase = 100
        b_intensity = self.triangle((i+160)%256)
        b_phase = 200
        
        def get_buffer(phase, intensity, velocity=1):
            buff = np.arange(self.N)
            buff = np.roll(buff, (phase+i*velocity)%self.N)
            buff = np.clip(np.sin(buff*(8*np.pi/self.N)),0,1)
            buff = (buff * intensity ).astype(np.uint8)
            return buff
        
        velocity=2
        self.video_buffer.buffer[0:len(self.video_buffer.buffer):3] = get_buffer(r_phase, r_intensity, 1)
        self.video_buffer.buffer[1:len(self.video_buffer.buffer):3] = get_buffer(g_phase, g_intensity, 2)
        self.video_buffer.buffer[2:len(self.video_buffer.buffer):3] = get_buffer(b_phase, b_intensity, 3)

        self.video_buffer.dirty = True
