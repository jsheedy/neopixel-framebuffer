from datetime import datetime

from .fx import Fx

class LarsonScanner(Fx):
    def __init__(self, video_buffer, n1=360, n2=410):
        self.video_buffer = video_buffer
        self.n1 = n1
        self.n2 = n2
        self.pos = n1 + abs(n2 - n1)
        self.bpm = 120
        self.count = 1
        self.timestamp = datetime(2000,1,1)
        self.velocity = 2

    def metronome(self, bpm, count):
        self.timestamp = datetime.now()
        self.bpm = int(bpm)
        self.count = int(count)

    def update(self):
        super(LarsonScanner, self).update()
        if not self.enabled:
            return
        
        if (datetime.now() - self.timestamp).seconds > 2:
            if self.pos >= self.n2-2:
                self.velocity = -2

            if self.pos <= self.n1+2:
                self.velocity = 2

            self.pos += self.velocity
        else:

            secs = (datetime.now() - self.timestamp).total_seconds()
            delta_beat = secs / (60/self.bpm)
            if self.count in (1,3):
                self.pos = int(self.n1 + (self.n2 - self.n1) * delta_beat)
            else:
                self.pos = int(self.n2 - (self.n2 - self.n1) * delta_beat)

        if self.pos > self.n2:
            self.pos = self.n2-2
        if self.pos < self.n1:
            self.pos = self.n1

        self.video_buffer.buffer[self.pos*3:self.pos*3+3] = (255,0,0)
        self.video_buffer.buffer[(self.pos-1)*3:(self.pos-1)*3+3] = (35,0,0)
        self.video_buffer.buffer[(self.pos+1)*3:(self.pos+1)*3+3] = (35,0,0)
        self.video_buffer.dirty = True
