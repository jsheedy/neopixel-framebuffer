#!/usr/bin/env python3

import itertools
import time

from pythonosc import dispatcher
from pythonosc import osc_server

from pythonosc import osc_message_builder
from pythonosc import udp_client

ip = "127.0.0.1"
port = 37340

client = udp_client.UDPClient(ip, port)

def midi_note_on(note):
    msg = osc_message_builder.OscMessageBuilder(address = "/midi/note")
    msg.add_arg(note)
    msg.add_arg(127)
    msg.add_arg(1)
    msg = msg.build()
    client.send(msg)

def midi_note_off(note):
    msg = osc_message_builder.OscMessageBuilder(address = "/midi/note")
    msg.add_arg(note)
    msg.add_arg(0)
    msg.add_arg(1)
    msg = msg.build()
    client.send(msg)

while True:
    for note in range(128):
        midi_note_on(note)
        time.sleep(0.05)
        midi_note_off(note)
        # time.sleep(0.05)