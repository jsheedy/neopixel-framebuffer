#!/usr/bin/env python3

"""Runs an event loop, pushing the one dimensional RGB data from VideoBuffer.buffer over a serial
line to an Arduino waiting to map those values to a NeoPixel strip.
A thread also listens for incoming OSC messages to control the buffer"""

import asyncio
import functools
import logging
from queue import Queue
import sys
import threading

import fx
from osc import OSCServer
import serial_comms
from touch_osc import accxyz
from video_buffer import VideoBuffer
import websocket_server
import midi

logging.basicConfig(level=logging.INFO)

N = 420

video_buffer = VideoBuffer(N)
midi_queue = Queue()

def osc_logger(*args):
    logging.debug(args)

def read_stdin():
    line = sys.stdin.readline().strip()
    fx = video_buffer.effects.get(line)
    if fx:
        fx.toggle()
        logging.info('toggled f/x {} {}'.format(fx, fx.enabled))
    elif line[:4] == 'fade':
        _, fade_amount = line.split()
        fade = video_buffer.effects['fade']
        fade.q = int(fade_amount)
    else:
        logging.info('unknown f/x {}'.format(line))
    print('all f/x:')

    print('{0:20} enabled'.format('f/x'))
    print('-'*30)
    for fx in video_buffer.effects.keys():
        print('{0:20} {1}'.format(fx, video_buffer.effects[fx].enabled))


def main():
    # effects['background'] = fx.BackGround(video_buffer, color='')
    video_buffer.add_effect('fade', fx.FadeBackGround, q=25)
    video_buffer.add_effect('wave', fx.Wave, enabled=False)
    video_buffer.add_effect('midi_note', fx.MidiNote, range=(310, 410))
    # add_effect('pointX'] = fx.PointFx(video_buffer, range=(360,420))
    # add_effect('pointY'] = fx.PointFx(video_buffer)
    # add_effect('pointZ'] = fx.PointFx(video_buffer)
    video_buffer.add_effect('scanner', fx.LarsonScanner, enabled=True, scanners=(
        {'n1':20, 'n2':45, 'color': (1, .5, 0)},
        {'n1':150,'n2':170, 'color': (0, 1, 0)},
        {'n1':250,'n2':290, 'color': (0, 0, 1)},
        # {'n1':360,'n2':400},
    ))
    video_buffer.add_effect('peak_meter', fx.PeakMeter, enabled=True, meters=(
        {'n1': 340, 'n2': 420, 'reverse': True},
        {'n1': 0, 'n2': 100, 'reverse': False},
    ))

    # midi_thread = threading.Thread(target=midi.main,kwargs={'q':midi_queue})
    # midi_thread.daemon = True
    # midi_thread.start()

    loop = asyncio.get_event_loop()

    loop.add_reader(sys.stdin.fileno(), read_stdin)

    websocket_server.serve(loop, video_buffer)
    serial_comms.init(loop, video_buffer)

    osc_server = OSCServer(
        loop = loop,
        maps = (
            ('/metronome', video_buffer.effects['scanner'].metronome),
            ('/audio/envelope', video_buffer.effects['peak_meter'].envelope),
            # ('/bassnuke', video_buffer.keyframes),
            ('/midi/note', video_buffer.effects['midi_note'].set),
            # ('/accxyz', functools.partial(accxyz, axis=0, point=effects['pointX'])),
            # ('/1/fader1', effects['background'].red),
            # ('/1/fader2',  effects['background'].green),
            # ('/1/fader3',  effects['background'].blue),
            ('/*', osc_logger),
        )
    )

    osc_server.serve()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

if __name__ == "__main__":
    main()
