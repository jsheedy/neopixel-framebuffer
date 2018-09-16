import colorsys
from datetime import datetime

import numpy as np

from .fx import Fx
from .point import PointFx
from .midi_event import MidiEvent


def make_key(note, channel):
    return "{}-{}".format(note, channel)


class MidiNoteSpark(Fx):
    velocity = 0
    channels = list(range(17))

    def __init__(self, video_buffer, **kwargs):
        self.nrange = kwargs.pop('nrange')
        super().__init__(video_buffer, **kwargs)
        self.points = {}

        for channel in self.channels:
            h = channel / len(self.channels)
            s = 1
            v = 1
            color = tuple(map(lambda x: int(x*255), colorsys.hsv_to_rgb(h, s, v)))

            # point = PointFx(video_buffer, nrange=self.nrange, color=color)
            # self.points.append(point)
        self.event_buffer = {}

    def set(self, addr, note, velocity, channel):
        key = make_key(note, channel)
        event = self.event_buffer.get(key)
        if event:
            if velocity == 0:
                del self.event_buffer[key]
                # del self.points[key]
                self.points[key]['t0'] = datetime.now()
            else:
                # keep it in the buffer, the note is still held
                event.velocity = velocity

        elif velocity > 0:
            # event isn't in buffer, add it
            event = MidiEvent(note, velocity, channel)
            self.event_buffer[key] = event
            h = channel / len(self.channels)
            s = 1
            v = 1
            color = tuple(map(lambda x: int(x*255), colorsys.hsv_to_rgb(h, s, v)))

            point = PointFx(self.video_buffer, nrange=self.nrange, color=color)
            t = datetime.now()
            # self.points[key + str(t)] = {'point': point, 'event': event, 't0': t}
            self.points[key] = {'point': point, 'event': event, 't0': t}

    def _update(self):
        midi_min = 40
        midi_max = 90
        midi_range = midi_max - midi_min
        items = list(self.points.items())
        for key, value in items:
            # note = np.clip(event.note, midi_min, midi_max)
            # note = event.note
            point = value['point']
            event = value['event']
            t0 = value['t0']

            delta_time = (datetime.now() - t0).total_seconds()

            scale = 1 / (1 + 2*delta_time)
            p = (event.note - midi_min) / midi_range

            if key not in self.event_buffer:
                p *= scale
                if delta_time > 4.0:
                    del self.points[key]

            point.set(p)
            point.intensity = event.velocity / 128

            h = scale # event.channel / len(self.channels)
            s = 1/scale
            v = 1/scale
            point.color = tuple(map(lambda x: int(x*255), colorsys.hsv_to_rgb(h, s, v)))

            point.update()

