import asyncio
import logging

from pythonosc import dispatcher
from pythonosc import osc_server


class OSCServer():

    def __init__(self, server_address, maps=None, forward=()):
        """
        maps - collection of (osc_address_string, handler) mappings
        forward - collection of methods to forward raw OSC datagrams to
        """
        self.maps = maps
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

        loop = asyncio.get_event_loop()
        listen = loop.create_datagram_endpoint(
            lambda: _OSCProtocolFactory(dsp, self),
            local_addr = self.server_address
        )
        logging.info("OSCServer listening on {}".format(self.server_address))
        return listen
