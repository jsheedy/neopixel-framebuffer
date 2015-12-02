import numpy as np

from .fx import Fx
from .point import PointFx


class MidiEvent():
    def __init__(self, note, velocity, channel):
        self.note = note
        self.velocity = velocity
        self.channel = channel

def make_key(note, channel):
    return "{}-{}".format(note, channel)

class MidiNote(Fx):
    velocity = 0
    channels = list(range(16))

    def __init__(self, video_buffer, **kwargs):
        range = kwargs.pop('range')
        super().__init__(video_buffer, **kwargs)
        self.points = [PointFx(video_buffer, range=range) for channel in self.channels]
        self.points[1].color = (255,255,255)
        self.points[2].color = (255,0,0)
        self.event_buffer = {}

    def set(self, addr, note, velocity, channel):
        key = make_key(note, channel)
        event = self.event_buffer.get(key)
        if event:
            if velocity == 0:
                del self.event_buffer[key]
            else:
                # keep it in the buffer, the note is still held
                event.velocity = velocity

        elif velocity > 0:
            # event isn't in buffer, add it
            self.event_buffer[key] = MidiEvent(note, velocity, channel)

    def update(self):
        super(MidiNote, self).update()
        midi_min = 24
        midi_max = 120
        for key, event in self.event_buffer.items():
            note = np.clip(event.note, midi_min, midi_max)
            p = note / (midi_max - midi_min)
            self.points[event.channel].set(p)
            self.points[event.channel].update()
