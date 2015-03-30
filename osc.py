import logging

logger = logging.getLogger()

class OSCServer():

    ip = "0.0.0.0"
    port = 37337

    def __init__(
        self,
        video_buffer=None,
        effects=None,
        maps=None):

        self.video_buffer=video_buffer
        self.effects = effects
        self.maps = maps or []
        self.background=effects.get('background')
        self.peak_meter=effects.get('peak_meter')
        self.peak_meter2=effects.get('peak_meter2')
        self.scanners=effects.get('scanners')
        self.midi_note=effects.get('midi_note')

    def color(self, name, channel, r,g,b):
        self.background.red(r)
        self.background.green(g)
        self.background.blue(b)

    def midinote(self, k, note, velocity, channel):
        if not self.midi_note:
            return
        print("%d %d" % (note,velocity))
        self.midi_note.set(note, velocity)

    def bassnuke(self, arg):
        print("NUKE")
        self.video_buffer.keyframes()

    def envelope(self, name, y, channel ):
        if not (self.peak_meter and self.peak_meter2):
            return

        y = float(y)

        channel = int(channel)
        if channel == 1:
            self.peak_meter.set(float(y))
        elif channel == 2:
            self.peak_meter2.set(float(y))

    def fader_green(self,v):
        self.background.green(v)

    def fader_blue(self,v):
        self.background.blue(v)

    def fader_red(self,v):
        self.background.red(v)

    def serve(self):
        from pythonosc import dispatcher
        from pythonosc import osc_server

        dispatcher = dispatcher.Dispatcher()

        for map in self.maps:
            dispatcher.map(map[0], map[1])

        dispatcher.map("/color/sky", self.color)
        dispatcher.map("/audio/envelope", self.envelope or logger.debug)
        dispatcher.map("/bassnuke", self.bassnuke)
        dispatcher.map("/midi/note", self.midinote)
        dispatcher.map("/1/fader1", self.fader_red)
        dispatcher.map("/1/fader2", self.fader_green)
        dispatcher.map("/1/fader3", self.fader_blue)

        server = osc_server.ThreadingOSCUDPServer((self.ip, self.port), dispatcher)
        print("Serving on {}".format(server.server_address))
        server.serve_forever()
