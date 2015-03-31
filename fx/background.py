import numpy as np

from .fx import Fx

class BackGround(Fx):

    def __init__(self, video_buffer, color=None, intensity=50):
        self.video_buffer = video_buffer
        self.color = color
        self.intensity = intensity

    # def red(self, x):
    #     N = self.video_buffer.N
    #     self.bgbuffer[0:N*3:3] = int(x*255)

    # def green(self, x):
    #     N = self.video_buffer.N
    #     self.bgbuffer[1:N*3:3] = int(x*255)

    def blue(self, x):
        N = self.video_buffer.N
        self.video_buffer.buffer[:] = 0
        self.video_buffer.buffer[2:N*3:3] = int(self.intensity*x*255)

    def clear(self, x):
        N = self.video_buffer.N
        self.video_buffer.buffer[:] = 0

    def update(self):
        super(BackGround, self).update()
        if not self.enabled:
            return
        if self.color == 'blue':
            self.blue(1.0)
        else:
            self.clear(self)