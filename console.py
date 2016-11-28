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

    elif line[:6] == 'bright':
        _, brightness = line.split()
        bright = _video_buffer.effects['brightness']
        bright.level = float(brightness)
        print("set brightness to {}".format(brightness))

    elif line[:3] == 'bpm':
        _, bpm = line.split()
        scanner = _video_buffer.effects['scanner']
        scanner.bpm = int(bpm)

    elif line[:3] == 'rgb':
        _, r, g, b = line.split()
        N = _video_buffer.N
        _video_buffer.buffer[0:N*3:3] = int(r)
        _video_buffer.buffer[1:N*3:3] = int(g)
        _video_buffer.buffer[2:N*3:3] = int(b)

    elif line == 'noise':
        _video_buffer.effects['noise'].enabled = True

    elif line == 'yellowblackandredgreenpurple':

        _video_buffer.buffer[:] = 0
        _video_buffer.buffer[300*3:320*3] = [255,255,0] * 20
        _video_buffer.buffer[320*3:340*3] = [0,0,0] * 20
        _video_buffer.buffer[340*3:360*3] = [255,0,0] * 20
        _video_buffer.buffer[360*3:380*3] = [0,255,0] * 20
        _video_buffer.buffer[380*3:400*3] = [102,51,153] * 20

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
