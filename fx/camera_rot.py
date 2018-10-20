import numpy as np

from .fx import Fx


class CameraRot(Fx):

    def __init__(self, video_buffer, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.is_post_process = True

    def _update(self):
        roll = int((np.sin(self.video_buffer.t) / 2 + 0.5) * 0.1 * self.video_buffer.resolution)
        return np.roll(self.video_buffer.buffer, roll, axis=0)