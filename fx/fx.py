from datetime import datetime
import logging

import numpy as np


class Fx(object):

    def __init__(self, video_buffer, enabled=True):
        self.video_buffer = video_buffer
        self.enabled = enabled
        self.timestamp = datetime(2000,1,1)
        self.parameters = dict()
        self.N = video_buffer.resolution
        self.x = np.zeros(shape=(self.N,3))
        self.x[:] = np.expand_dims(np.arange(self.N),axis=0).T


    def __str__(self):
        return self.__class__.__name__


    def update(self):
        if not self.enabled:
            return False
        else:
            return self._update()


    def toggle(self):
        self.enabled = not self.enabled