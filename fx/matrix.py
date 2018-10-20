import numpy as np

from .fx import Fx


class Matrix(Fx):
    s = .5 / np.sqrt(2)
    S = np.matrix([
        [s, 0, 0],
        [0, s, 0],
        [0, 0, s]
    ])
    S_I = S.I
    T = np.matrix([
        [1, 0, .5],
        [0, 1, .5],
        [0, 0, .5],
    ])
    T_I = T.I
    def __init__(self, video_buffer, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.is_post_process = True

    def _update(self):
        theta = self.video_buffer.t / (2*np.pi)
        # theta = self.video_buffer.delta_time * 2 * np.pi
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

        R = Rz * Ry * Rx
        Z = R * self.T * self.S * np.matrix(self.video_buffer.buffer).T
        return (self.S_I * self.T_I * Z).T.A
