import time

import rtmidi
# import rtmidi_python as rtmidi


class MidiInputHandler():
    def __init__(self, port, q=None):
        self.port = port
        self._wallclock = time.time()
        self.q = q

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))
        unknown, cc, value = message
        if cc == 32:
            self.q.put({'key':'wave', 'value': value})
        elif cc == 33:
            self.q.put({'key':'scanner', 'value': value})

def callback(message, time_stamp):
    # format changed..
    print(message, time_stamp)

def main(q=None):
    port = 0
    try:
        midi_in = rtmidi.MidiIn()
        midi_in.open_port(0)
        # midiin, port_name = open_midiport(port)
        # midi_in.set_callback(MidiInputHandler(port_name, q=q))
        print("Attaching MIDI input callback handler.")
        midi_in.callback = callback
    except:
        print("no MIDI device")
        return

    print("Entering main loop. Press Control-C to exit.")
    try:
        # just wait for keyboard interrupt in main thread
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('')
    finally:
        print("Exit.")
        midiin.close_port()
        del midiin

