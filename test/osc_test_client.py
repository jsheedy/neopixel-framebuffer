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

def metronome(bpm=120, beat=1):
    msg = osc_message_builder.OscMessageBuilder(address = "/metronome")
    msg.add_arg(bpm)
    msg.add_arg(beat)
    msg = msg.build()
    client.send(msg)

def bass_nuke():
    msg = osc_message_builder.OscMessageBuilder(address = "/bassnuke")
    msg = msg.build()
    client.send(msg)

def color_ramp():
    r = 0
    g = 0
    b = 0

    for i in range(1,4):
        for j in itertools.chain(range(0, 255, 4),range(255,0,-4)):

            if i==1:
                g=b=0
                r=j
            elif i==2:
                r=b=0
                g=j
            elif i==3:
                r=g=0
                b=j
            msg = osc_message_builder.OscMessageBuilder(address = "/color/sky")
            msg.add_arg('wtf')
            msg.add_arg('color')
            msg.add_arg(r)
            msg.add_arg(g)
            msg.add_arg(b)
            msg = msg.build()
            client.send(msg)
            time.sleep(.02)


bass_nuke()


def envelope():
    N = 20
    for i in range(0,N):
        msg = osc_message_builder.OscMessageBuilder(address = "/audio/envelope")
        msg.add_arg(i/N)
        msg.add_arg(1)
        msg = msg.build()
        client.send(msg)
        time.sleep(.05)

# .color_ramp()
# time.sleep(.5)
while True:
    envelope()
    # for i in range(1,5):
        # metronome(bpm=120, beat=i)
        # time.sleep(.5)
