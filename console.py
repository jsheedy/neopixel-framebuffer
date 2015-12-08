import logging
import sys

_video_buffer = None

def read_stdin():
    line = sys.stdin.readline().strip()
    fx = _video_buffer.effects.get(line)
    if fx:
        fx.toggle()
        logging.info('toggled f/x {} {}'.format(fx, fx.enabled))
    elif line[:4] == 'fade':
        _, fade_amount = line.split()
        fade = _video_buffer.effects['fade']
        fade.q = int(fade_amount)
    elif line[:3] == 'bpm':
        _, bpm = line.split()
        scanner = _video_buffer.effects['scanner']
        scanner.bpm = int(bpm)
    else:
        logging.info('unknown f/x {}'.format(line))
    print('all f/x:')

    print('{0:20} enabled'.format('f/x'))
    print('-'*30)
    for fx in _video_buffer.effects.keys():
        print('{0:20} {1}'.format(fx, _video_buffer.effects[fx].enabled))

def init(loop, video_buffer):
    global _video_buffer
    _video_buffer = video_buffer
    loop.add_reader(sys.stdin.fileno(), read_stdin)
