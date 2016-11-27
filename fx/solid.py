from .fx import Fx

class Solid(Fx):

    def __init__(self, video_buffer, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.video_buffer.buffer[0:self.video_buffer.N*3:3] = 255

    def _update(self):
        pass