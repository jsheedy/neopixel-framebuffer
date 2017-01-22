from .fx import Fx
from point import Point

import numpy as np


class PointFx(Fx):
    enabled = True
    position = 0.0
    intensity = 1.0

    def __init__(self, video_buffer, color=(255,255,255), nrange=None, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.point = Point(0, nrange[1] - nrange[0])
        # self.point = Point(0, video_buffer.N)

        self.range = nrange or (0, video_buffer.N)
        self.color = color
        self.p0 = self.range[0] / self.video_buffer.N
        self.p1 = self.range[1] / self.video_buffer.N

    def project(self, position):
        """ take position from 0->1 and map to video_buffer range """
        return self.p0 + position * (self.p1-self.p0)

    def set(self, position):
        # self.position = self.project(position)
        self.point.pos = self.project(position)

    def _update(self):
        N = self.video_buffer.N
        # self.point.pos = self.position
        points = self.point.get_points()

        r_arr = self.color[0]*self.intensity*points
        b_arr = self.color[1]*self.intensity*points
        g_arr = self.color[2]*self.intensity*points
        arr = np.vstack((r_arr, g_arr, b_arr)).reshape((-1,), order='F')
        self.video_buffer.merge(self.range[0], self.range[1], arr)
