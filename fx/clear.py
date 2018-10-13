from .fx import Fx


class Clear(Fx):

    def _update(self):
        self.video_buffer.buffer[:] = 0.0