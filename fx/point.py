from .fx import Fx
from point import Point

class PointFx(Fx):
    enabled = True
    position = 0

    def __init__(self, video_buffer, color=(255,255,255), range=None):
        super().__init__(video_buffer)
        self.point = Point(0, video_buffer.N)
        self.range = range or (0, video_buffer.N)
        self.color = [c/255.0 for c in color]
        self.p0 = self.range[0] / self.video_buffer.N
        self.p1 = self.range[1] / self.video_buffer.N

    def project(self, position):
        """ take position from 0->1 and map to entire video_buffer range """
        return self.p0 + position * (self.p1-self.p0)

    def set(self, position):
        self.position = self.project(position)

    def update(self):
        super(PointFx, self).update()
        N = self.video_buffer.N
        if self.position > 1:
            self.position=0
        self.point.pos = self.position
        points = self.point.get_points()
        for i,color in enumerate(self.color):
            if i == 0:
                self.video_buffer.buffer[i:N*3:3][points>0] = color*points[points>0]
