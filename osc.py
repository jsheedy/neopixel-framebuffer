import logging

from pythonosc import dispatcher
from pythonosc import osc_server

class OSCServer():

    ip = "0.0.0.0"
    port = 37337

    def __init__(self, loop=None, maps=None):
        self.maps = maps
        self.loop = loop

    def serve(self):

        dsp = dispatcher.Dispatcher()

        for map in self.maps:
            dsp.map(map[0], map[1])

        # server = osc_server.ThreadingOSCUDPServer((self.ip, self.port), dsp)
        server = osc_server.AsyncIOOSCUDPServer((self.ip, self.port), dsp, self.loop)
        print("Serving on {}:{}".format(self.ip, self.port))
        server.serve()
        # server.serve_forever()
