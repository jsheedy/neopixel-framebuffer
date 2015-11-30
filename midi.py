import queue
import time
import rtmidi
from rtmidi.midiutil import open_midiport

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

def main(q=None):
    port = 0
    try:
        midiin, port_name = open_midiport(port)
    except:
        print("no MIDI device")
        return

    print("Attaching MIDI input callback handler.")
    midiin.set_callback(MidiInputHandler(port_name, q=q))

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

