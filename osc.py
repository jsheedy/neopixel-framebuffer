import logging

from pythonosc import dispatcher
from pythonosc import osc_server

class OSCServer():

    ip = "0.0.0.0"
    port = 37337

    def __init__(self, maps=None):
        self.maps = maps

    def serve(self):

        dsp = dispatcher.Dispatcher()

        for map in self.maps:
            dsp.map(map[0], map[1])

        server = osc_server.ThreadingOSCUDPServer((self.ip, self.port), dsp)
        print("Serving on {}".format(server.server_address))
        server.serve_forever()
