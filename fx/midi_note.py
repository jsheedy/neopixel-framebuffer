import numpy as np

from point import Point
from .fx import Fx
from .midi_event import MidiEvent


def make_key(note, channel):
    return "{}-{}".format(note, channel)


colors = [
    (.8, .2, .1),
    (.3, .8, .3),
    (.7, .2, .8),
    (.1, .2, .3),
    (.9, .2, .4),
    (.8, .6, .1),
    (.9, .2, .1),
    (.5, .0, .6),
]

class MidiNote(Fx):
    velocity = 0
    channels = list(range(17))


    def __init__(self, video_buffer, **kwargs):
        self.nrange = kwargs.pop('nrange')
        super().__init__(video_buffer, **kwargs)
        self.points = []
        self.length = self.nrange[1] - self.nrange[0]

        for _channel in self.channels:
            point = Point(0, video_buffer.resolution, width=0.02)
            self.points.append(point)
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


    def _update(self):
        midi_min = 12
        midi_max = 115
        midi_range = midi_max - midi_min

        self.x[:] = 0
        for key, event in self.event_buffer.items():
            note = event.note
            absolute_position = np.clip((note - midi_min) / midi_range, 0, 1)
            relative_position = self.nrange[0] + absolute_position*self.length
            point = self.points[event.channel]
            point.pos = relative_position
            intensity = event.velocity / 128
            r,g,b = colors[event.channel]
            points = point.get_points()
            self.x[:,0] += r * intensity * points
            self.x[:,1] += g * intensity * points
            self.x[:,2] += b * intensity * points

        return self.x
