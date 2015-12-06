#!/usr/bin/env python3

import itertools
import time

from pythonosc import dispatcher
from pythonosc import osc_server

from pythonosc import osc_message_builder
from pythonosc import udp_client

ip = "127.0.0.1"
port = 37337

client = udp_client.UDPClient(ip, port)

def midi_note_on():
    msg = osc_message_builder.OscMessageBuilder(address = "/midi/note")
    msg.add_arg(65)
    msg.add_arg(127)
    msg.add_arg(1)
    msg = msg.build()
    client.send(msg)

def midi_note_off():
    msg = osc_message_builder.OscMessageBuilder(address = "/midi/note")
    msg.add_arg(65)
    msg.add_arg(0)
    msg.add_arg(1)
    msg = msg.build()
    client.send(msg)


midi_note_on()
time.sleep(1)
midi_note_off()
