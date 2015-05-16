import logging

from pythonosc import dispatcher
from pythonosc import osc_server

class OSCServer():

    def __init__(self, server_address=("0.0.0.0", 37337), loop=None, maps=None):
        self.maps = maps
        self.loop = loop
        self.server_address = server_address

    def serve(self):

        dsp = dispatcher.Dispatcher()

        for map in self.maps:
            dsp.map(map[0], map[1])

        server = osc_server.AsyncIOOSCUDPServer(self.server_address, dsp, self.loop)
        logging.info("AsyncIOOSCUDPServer listening on {}".format(self.server_address))
        server.serve()
