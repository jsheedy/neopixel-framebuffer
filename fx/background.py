from .fx import Fx


class BackGround(Fx):

    def __init__(self, video_buffer, color=(255, 0, 0), intensity=50, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.color = color
        self.intensity = intensity
        self.N = self.video_buffer.N

    def red(self, x):
        N = self.video_buffer.N
        self.bgbuffer[0:N*3:3] = int(x*255)

    def green(self, x):
        N = self.video_buffer.N
        self.bgbuffer[1:N*3:3] = int(x*255)

    def blue(self, x):
        N = self.video_buffer.N
        self.video_buffer.buffer[:] = 0
        self.video_buffer.buffer[2:N*3:3] = int(self.intensity*x*255)

    def clear(self, x):
        self.video_buffer.buffer[:] = 0

    def _update(self):
        if self.color:
            r,g,b = self.color
            self.video_buffer.buffer[0:self.N*3:3] = int(self.intensity*r)
            self.video_buffer.buffer[1:self.N*3:3] = int(self.intensity*g)
            self.video_buffer.buffer[2:self.N*3:3] = int(self.intensity*b)

        else:
            self.clear(self)
