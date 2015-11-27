from .fx import Fx

class MidiNote(Fx):
    enabled = True
    note = 0
    velocity = 0

    def set(self, note, velocity):
        self.note = note
        self.velocity = velocity

    def update(self):
        super(MidiNote, self).update()
        i = self.note % 12
        multiplier = self.video_buffer.N / 12
        n = int(i * multiplier)
        self.video_buffer.buffer[n*3:n*3+3] = (255,255,255)
