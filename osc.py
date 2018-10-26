import asyncio
import logging

from pythonosc import dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer


class OSCServer():

    def __init__(self, server_address, maps=None):
        """
        maps - collection of (osc_address_string, handler) mappings
        forward - collection of methods to forward raw OSC datagrams to
        """
        self.maps = maps
        self.server_address = server_address
        loop = asyncio.get_event_loop()
        dsp = dispatcher.Dispatcher()
        for map in self.maps:
            dsp.map(map[0], map[1], needs_reply_address=(len(map)==3))
        self.server = AsyncIOOSCUDPServer(server_address, dsp, loop)

    def serve(self):

        logging.info("OSCServer listening on {}".format(self.server_address))
        return self.server.create_serve_endpoint()
