class PeakMeter(object):
    def __init__(self, video_buffer, n1=280, n2=320,reverse=False):
        self.video_buffer = video_buffer
        self.n1 = n1
        self.n2 = n2
        self.reverse = reverse
        self.set(0)
        self.level = 0.0
        self.last_y = 0

    def set(self, level):
        """level 0 -> 1"""
        self.level = level

    def update(self):

        y = int(self.level * (self.n2 - self.n1))

        if not self.reverse:
            self.video_buffer.buffer[self.n1*3:(self.n1+self.last_y)*3] = (100,62,0)*(self.last_y)
            self.video_buffer.buffer[self.n1*3:(self.n1+y)*3] = (0,155,0)*y
        else:
            self.video_buffer.buffer[self.n2*3-1:(self.n2-self.last_y)*3-1:-1] = (100,65,0)*self.last_y
            self.video_buffer.buffer[self.n2*3-1:(self.n2-y)*3-1:-1] = (0,155,0)*y

        self.last_y = y
        self.video_buffer.dirty = True

