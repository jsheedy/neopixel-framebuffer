from datetime import datetime
import logging

import numpy as np

logger = logging.getLogger(__name__)


class Fx(object):
    enabled = True

    def __init__(self, video_buffer, enabled=True):
        self.video_buffer = video_buffer
        self.enabled = enabled
        self.timestamp = datetime(2000,1,1)
        self.locked = False
        self.parameters = dict()
        self.N = video_buffer.N
        self.x = np.arange(self.N, dtype=np.float64)


    def __str__(self):
        return self.__class__.__name__

    def update(self):
        if (not self.enabled) \
            or (not self.locked and self.video_buffer.locked):
            # logger.debug('skipping update. locked: {} enabled: {}'.format(self.locked, self.enabled))
            return False
        else:
            self._update()

    def lock(self):
        self.locked = True
        self.video_buffer.locked = True

    def unlock(self):
        self.locked = False
        self.video_buffer.locked = False

    def toggle(self):
        self.enabled = not self.enabled