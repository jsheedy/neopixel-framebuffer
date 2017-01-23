from .fx import Fx


class BackGround(Fx):

    def __init__(self, video_buffer, color=None, intensity=1.0, **kwargs):
        super().__init__(video_buffer, **kwargs)
        self.color = color or [255, 0, 0]
        self.intensity = intensity
        self.N = self.video_buffer.N

    def set(self, addr, cc, value):
        if cc == 22:  # K1 knob
            self.color[0] = value * 2
        elif cc == 23:  # K2 knob
            self.color[1] = value * 2
        elif cc == 24:  # K3 knob
            self.color[2] = value * 2
        elif cc == 25:  # K4 knob
            self.intensity = value / 127

    def clear(self, x):
        self.video_buffer.buffer[:] = 0

    def _update(self):
        if self.color:
            r,g,b = self.color
            self.video_buffer.buffer[0:self.N*3:3] = int(self.intensity*r)
            self.video_buffer.buffer[1:self.N*3:3] = int(self.intensity*g)
            self.video_buffer.buffer[2:self.N*3:3] = int(self.intensity*b)

        else:
            self.clear(self)
