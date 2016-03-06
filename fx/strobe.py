import logging

from .fx import Fx


logger = logging.getLogger(__name__)


class Strobe(Fx):

    def __init__(self, video_buffer):
        super().__init__(video_buffer)
        self.frames = 0
        self.colors = (
            (255,255,255),
            (255,0,0),
            (0,255,0),
            (0,0,255),
        )

    def _update(self):
        if self.frames:
            self.frames -= 1

        elif self.locked:
            self.unlock()

    def metronome(self, _, bpm, count):
        logger.debug("strobe caught metronome: {}".format(bpm))
        if self.enabled:
            color = self.colors[int(count)-1]
            self.strobe(color=color)
        elif self.locked:
            self.unlock()

    def strobe(self, frames=20, color=(255,255,255)):
        # keep a strobe locked for frames frames
        self.frames = frames
        # self.lock()
        self.video_buffer.buffer[:] = color*self.video_buffer.N
