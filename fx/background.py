import numpy as np

class BackGround(object):


    def __init__(self, video_buffer):
        self.video_buffer = video_buffer
        self.bgbuffer = np.zeros(self.video_buffer.N*3, dtype=np.uint8)

    def red(self, x):
        N = self.video_buffer.N
        self.bgbuffer[0:N*3:3] = int(x*255)

    def green(self, x):
        N = self.video_buffer.N
        self.bgbuffer[1:N*3:3] = int(x*255)

    def blue(self, x):
        N = self.video_buffer.N
        self.bgbuffer[2:N*3:3] = int(x*255)

    def update(self):
        self.video_buffer.buffer = self.bgbuffer.copy()
        self.video_buffer.dirty = True