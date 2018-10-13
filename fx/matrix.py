import numpy as np

from .fx import Fx


class Matrix(Fx):

    def __init__(self, video_buffer, **kwargs):
        super().__init__(video_buffer, **kwargs)


    def _update(self):
        theta = self.video_buffer.delta_time
        Rx = np.matrix([
            [1, 0, 0],
            [0, np.cos(theta), -np.sin(theta)],
            [0, np.sin(theta), np.cos(theta)],
        ])
        Ry = np.matrix([
            [np.cos(theta), 0, np.sin(theta)],
            [0, 1, 0],
            [-np.sin(theta), 0, np.cos(theta)],
        ])
        Rz = np.matrix([
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta), np.cos(theta), 0],
            [0, 0, 1],
        ])
        s = .5 / np.sqrt(2)
        S = np.matrix([
            [s, 0, 0],
            [0, s, 0],
            [0, 0, s]
        ])
        T = np.matrix([
            [1, 0, .5],
            [0, 1, .5],
            [0, 0, .5],
        ])
        R = Rz * Ry * Rx
        Z = R * T * S * np.matrix(self.video_buffer.buffer).T
        self.video_buffer.buffer = (S.I * T.I * Z).T.A
