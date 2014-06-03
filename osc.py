
class OSCServer():

    ip = "0.0.0.0"
    port = 37337

    def __init__(
        self,
        video_buffer=None,
        effects=None):

        self.video_buffer=video_buffer
        self.effects = effects
        self.background=effects['background']
        self.peak_meter=effects['peak_meter']
        self.peak_meter2=effects['peak_meter2']
        self.scanner=effects['scanner']

    def metronome(self, x,  bpm, beat):
        self.scanner.metronome(bpm, beat)

    def color(self, name, channel, r,g,b):
        self.background.red(r)
        self.background.green(g)
        self.background.blue(b)

    def bassnuke(self, arg):
        print("NUKE")
        self.video_buffer.keyframes()
 
    def envelope(self, name, ychannel ):
        y,channel = ychannel.split()

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
        dispatcher.map("/metronome", self.metronome)
        dispatcher.map("/color/sky", self.color)
        dispatcher.map("/audio/envelope", self.envelope)
        dispatcher.map("/bassnuke", self.bassnuke)
        dispatcher.map("/1/fader1", self.fader_red)
        dispatcher.map("/1/fader2", self.fader_green)
        dispatcher.map("/1/fader3", self.fader_blue)

        server = osc_server.ThreadingOSCUDPServer((self.ip, self.port), dispatcher)
        print("Serving on {}".format(server.server_address))
        server.serve_forever()
