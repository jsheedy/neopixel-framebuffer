import numpy as np

from .fx import Fx


class Matrix(Fx):

    def __init__(self, video_buffer, **kwargs):
        super().__init__(video_buffer, **kwargs)


    # def set(self, addr, value, color :str ='r'):
    #     self.rgb[color] = value
    #     self.dirty = True


    def _update(self):
        theta = self.video_buffer.t / 10
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
        S = np.matrix([
            [0.5, 0, 0],
            [0, 0.5, 0],
            [0, 0, 0.5]
        ])
        T = np.matrix([
            [1, 0, .5],
            [0, 1, .5],
            [0, 0, .5],
        ])
        R = Rz  # Ry * Rz * Rx
        Z = R * T * S * np.matrix(self.video_buffer.buffer).T
        self.video_buffer.buffer = (S.I * T.I * Z).T.A
