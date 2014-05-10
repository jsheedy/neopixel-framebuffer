class PeakMeter(object):
    def __init__(self, video_buffer, n1=280, n2=320,reverse=False):
        self.video_buffer = video_buffer
        self.n1 = n1
        self.n2 = n2
        self.reverse = reverse
        self.set(0)
        self.level = 0.0

    def set(self, level):
        """level 0 -> 1"""
        self.level = level

    def update(self):

        lev = int((self.n2 - self.n1) *.8 )
        y = int(self.level * (self.n2 - self.n1))

        if not self.reverse:
            self.video_buffer.buffer[self.n1*3:(self.n1+y)*3] = (0,155,0)*y
            # if (self.level > .8):
                # video_buffer.buffer[(self.n1+lev)*3:(self.n1+y)*3] = (255,0,0)*(y-lev)
        else:
            self.video_buffer.buffer[self.n2*3-1:(self.n2-y)*3-1:-1] = (0,155,0)*y
            # if (self.level > .8):
                # video_buffer.buffer[(self.n2+lev)*3:(self.n2+y)*3:-1] = (255,0,0)*(y-lev)

        self.video_buffer.dirty = True

