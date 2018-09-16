class MidiEvent():
    def __init__(self, note, velocity, channel):
        self.note = note
        self.velocity = velocity
        self.channel = channel

    def __repr__(self):
        return f'Midi Event {self.note} - {self.velocity} - {self.channel}'

