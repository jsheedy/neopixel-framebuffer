from collections import OrderedDict

from .fx import Fx


class BackGround(Fx):

    def __init__(self, video_buffer, color=(1,0,0), **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.rgb = OrderedDict(zip('rgb', color))
        self.dirty = True

    def set(self, addr, value, color :str ='r'):
        self.rgb[color] = value
        self.dirty = True


    def _update(self):
        if self.dirty:
            self.x[:] = tuple(self.rgb.values())
            self.dirty = False
        return self.x