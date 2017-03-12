import asyncio
from datetime import datetime
import functools
import logging

import urwid

import log


osc_queue = None
logger = logging.getLogger()

palette = [
    ('header', 'black', 'light blue'),
    ('footer', 'black', 'light green'),
    ('columnheader', 'black', 'light gray'),
    ('paused', 'light red', 'white'),
    ('playing', 'dark green', 'black'),
]

play_pause_indicator = urwid.Text('PLAYING', align='center', wrap='clip')
play_pause_indicator_attr = urwid.AttrWrap(urwid.Padding(play_pause_indicator), 'playing')

_video_buffer = None

params_widgets = []
pixels = []
attr_specs = {}

urwid_loop = None

lw = urwid.SimpleListWalker([])
listbox = urwid.ListBox(lw)
listbox = urwid.AttrWrap(listbox, 'listbox')



@functools.lru_cache()
def get_attr(entry):
    """ caches AttrSpecs """
    foreground = "#fff"
    colors = 256
    if entry in attr_specs:
        return attr_specs[entry]
    else:
        attr = urwid.AttrSpec(foreground, entry, colors)
        attr_specs[entry] = attr
        return attr


def update_pixels(video_buffer):

    for i, pixel in enumerate(pixels):
        r,g,b = video_buffer.buffer[i*3:i*3+3]
        entry = "#" + "".join(["{:02x}".format(x)[0] for x in (r,g,b)])
        attr = get_attr(entry)
        pixel.set_attr_map({None: attr})


t0 = datetime.now()
epoch = datetime.now()
f0 = 0

def init_params(video_buffer):
    def fps():
        global t0
        global f0
        t1 = datetime.now()
        f1 = video_buffer.frame
        dt = (t1-t0).total_seconds()
        df = f1 - f0
        t0 = t1
        f0 = f1
        return "{:.1f} fps".format(df/dt)

    def runtime():
        t1 = datetime.now()
        dt = (t1-epoch).total_seconds()
        return "{:.1f}s".format(dt)

    parameters = (
        ("frame", "0", lambda: str(video_buffer.frame)),
        ("fps", "0", fps),
        ("runtime", "0", runtime)
    )

    for label, value, update_function in parameters:

        widget = urwid.Columns([
            urwid.Text(label, align='left'),
            urwid.Text(value, align='right'),
        ])
        widget.update_function = update_function
        params_widgets.append(widget)

    divider = urwid.Divider('-')
    widgets = [urwid.Padding(play_pause_indicator_attr), divider] + params_widgets + [divider, ]

    for i in range(video_buffer.N):
        foreground = "#fff"
        entry = "#" + ("{:02x}".format(i%256)[0]) * 3
        colors = 256
        attr = urwid.AttrSpec(foreground, entry, colors)
        text = urwid.Text(".")
        pixel = urwid.AttrMap(text, attr)
        pixels.append(pixel)
    pixel_grid_flow = urwid.GridFlow(pixels, 1, 0, 0, 'center')
    widgets.append(pixel_grid_flow)
    pile = urwid.Filler(urwid.Pile(widgets), valign='top')
    return pile


def column_header(text):
    widget = urwid.Text(text)
    widget_wrap = urwid.AttrWrap(widget, 'columnheader')
    return widget_wrap


def init_fx(video_buffer):
    header = column_header("f/x")
    widgets = [header,]

    def callback(cb, state, fx):
        fx.enabled = state

    for label, fx in video_buffer.effects.items():
        check_box = urwid.CheckBox(str(fx), state=fx.enabled)

        user_data = fx
        urwid.connect_signal(check_box, 'change', callback, user_data)

        widgets.append(check_box)
    pile = urwid.Filler(urwid.Pile(widgets), valign='top')
    return pile


def init_logs():
    return listbox


async def update_ui(video_buffer):

    while True:
        for param in params_widgets:
            widget, options = param.contents[1]
            text = param.update_function()
            widget.set_text(text)

        update_pixels(video_buffer)
        await asyncio.sleep(0.2)


async def osc_handler():

    while True:
        osc = await osc_queue.get()
        message = "OSC: {}".format(osc)
        lw.append(urwid.Text(message))
        lw.append(urwid.Divider('-'))
        listbox.set_focus(len(lw) - 1, 'above')


async def log_handler():

    while True:
        log_record = await log.queue.get()
        message = "{}:{} {}".format(log_record.filename, log_record.lineno, log_record.message)
        if log_record.exc_info:
            message += str(log_record.exc_info)

        lw.append(urwid.Text(message))
        lw.append(urwid.Divider('-'))
        listbox.set_focus(len(lw) - 1, 'above')


def urwid_console(video_buffer):

    header = urwid.Text("NEOPIXEL FRAMEBUFFER", align='center')
    header = urwid.AttrWrap(header, 'header')

    footer = urwid.Text("keys: (q)uit, (p)ause/resume, (c)lear")
    footer = urwid.AttrWrap(footer, 'footer')

    params = init_params(video_buffer)
    plays = init_fx(video_buffer)

    body = urwid.Columns((
        ('weight', 1, params),
        ('weight', 1, plays),
        ('weight', 1, listbox),
    ), dividechars=3)

    frame = urwid.Frame(body, header=header, footer=footer)
    return frame


def show_or_exit(key):

    if key in ('p', 'P'):
        _video_buffer.enabled = not _video_buffer.enabled
        msg = _video_buffer.enabled and "PLAYING" or "PAUSED"
        logger.info(msg)
        play_pause_indicator.set_text(msg)
        play_pause_indicator_attr.set_attr(msg.lower())

    elif key in ('q', 'Q'):
        for task in asyncio.Task.all_tasks():
            task.cancel()
        urwid_loop.stop()
        asyncio.get_event_loop().stop()


def osc_recv(*args):
    osc_queue.put_nowait(args)


def init(loop, video_buffer):
    global _video_buffer
    global osc_queue
    osc_queue = asyncio.Queue(loop=loop)
    _video_buffer = video_buffer
    colors = 256
    asyncio.ensure_future(log_handler())
    asyncio.ensure_future(osc_handler())
    asyncio.ensure_future(update_ui(video_buffer))
    global urwid_loop
    urwid_loop = urwid.MainLoop(urwid_console(video_buffer), palette, event_loop=urwid.AsyncioEventLoop(), unhandled_input=show_or_exit)
    screen = urwid_loop.screen
    screen.set_terminal_properties(colors)
    urwid_loop.start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    from video_buffer import VideoBuffer

    init(loop, VideoBuffer(N=420))
