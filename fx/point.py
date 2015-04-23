from .fx import Fx
from point import Point

class PointFx(Fx):
    enabled = True
    position = 0

    def __init__(self, video_buffer, axis=0):
        super().__init__(video_buffer)
        self.axis = axis

    def set(self, position):
        self.position = position

    def xyz(self, addr, *args):
        """self, addr, x, y, z"""

        pos = (args[self.axis] + 1) / 2
        print ("{} ".format(args))
        self.set(pos)

    def update(self):
        N = self.video_buffer.N
        super(PointFx, self).update()
        # offset = self.position * self.video_buffer.N
        point = Point(self.position, N)
        points = point.get_points(margin=0)
        self.video_buffer.buffer[self.axis:N*3:3] += points
