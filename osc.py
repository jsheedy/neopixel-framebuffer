import asyncio
import logging

from pythonosc import dispatcher
from pythonosc import osc_server

class OSCServer():

    def __init__(self, server_address, loop=None, maps=None, forward=()):
        """
        loop - asyncio event loop
        maps - collection of (osc_address_string, handler) mappings
        forward - collection of methods to forward raw OSC datagrams to
        """
        self.maps = maps
        self.loop = loop
        self.server_address = server_address
        self.forward = forward

    def serve(self):

        dsp = dispatcher.Dispatcher()

        for map in self.maps:
            dsp.map(map[0], map[1])

        class _OSCProtocolFactory(asyncio.DatagramProtocol):
          """OSC protocol factory which passes datagrams to _call_handlers_for_packet"""

          def __init__(self, dispatcher, server):
            self.dispatcher = dispatcher
            self.server = server

          def datagram_received(self, data, _unused_addr):
            osc_server._call_handlers_for_packet(data, self.dispatcher)
            for f in self.server.forward:
                f(data)

        listen = self.loop.create_datagram_endpoint(
            lambda: _OSCProtocolFactory(dsp, self),
            local_addr = self.server_address
        )
        self.loop.run_until_complete(listen)
        logging.info("OSCServer listening on {}".format(self.server_address))
