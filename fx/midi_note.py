import colorsys

import numpy as np

from .fx import Fx
from .point import PointFx


class MidiEvent():
    def __init__(self, note, velocity, channel):
        self.note = note
        self.velocity = velocity
        self.channel = channel

    def __repr__(self):
        return f'Midi Event {self.note} - {self.velocity} - {self.channel}'


def make_key(note, channel):
    return "{}-{}".format(note, channel)


class MidiNote(Fx):
    velocity = 0
    channels = list(range(17))
    points = []

    def __init__(self, video_buffer, **kwargs):
        nrange = kwargs.pop('nrange')
        super().__init__(video_buffer, **kwargs)

        for channel in self.channels:
            h = channel / len(self.channels)
            s = 1
            v = 1
            color = tuple(map(lambda x: int(x*255), colorsys.hsv_to_rgb(h, s, v)))

            point = PointFx(video_buffer, nrange=nrange, color=color)
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
        midi_min = 0
        midi_max = 127
        midi_range = midi_max - midi_min

        for key, event in self.event_buffer.items():
            # note = np.clip(event.note, midi_min, midi_max)
            notes = event.note
            p = note / midi_range
            point = self.points[event.channel]
            point.set(p)
            point.intensity = event.velocity / 128
            point.update()
