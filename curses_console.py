import asyncio
from datetime import datetime
import functools
import logging

import sounddevice
import urwid

import audio_input
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

colors = 256
params_widgets = []
pixel_check_box = None
pixels = []

urwid_loop = None

SLEEP_TIME = 0.25

lw = urwid.SimpleListWalker([])
listbox = urwid.ListBox(lw)
listbox = urwid.AttrWrap(listbox, 'listbox')

osc_widget = None


@functools.lru_cache()
def get_attr(rgb):
    """ caches AttrSpecs """
    foreground = "#fff"
    colors = 256
    entry = "#" + "".join(["{:02x}".format(x)[0] for x in rgb])
    return {None: urwid.AttrSpec(foreground, entry, colors)}


async def update_pixels(video_buffer):
    for i, pixel in enumerate(pixels):
        rgb = tuple(video_buffer.buffer[i*3:i*3+3])
        attr = get_attr(rgb)
        pixel.set_attr_map(attr)


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

    for i in range(video_buffer.N):
        attr = get_attr((0,0,0))
        text = urwid.Text("`")
        pixel = urwid.AttrMap(text, attr)
        pixels.append(pixel)
    pixel_grid_flow = urwid.GridFlow(pixels, 1, 0, 0, 'center')

    global pixel_check_box
    pixel_check_box = urwid.CheckBox("RENDER PIXELS", state=True)

    widgets = [urwid.Padding(play_pause_indicator_attr), divider] + \
        params_widgets + \
        [divider, pixel_check_box, pixel_grid_flow]


    pile = urwid.Filler(urwid.Pile(widgets), valign='top')
    return pile


def column_header(text):
    widget = urwid.Text(text)
    widget_wrap = urwid.AttrWrap(widget, 'columnheader')
    return widget_wrap


def init_osc():
    global osc_widget
    header = column_header("OSC")
    text_widget = urwid.AttrWrap(urwid.Text("OSC"), 'listbox')
    osc_widget = urwid.Pile([text_widget])
    widgets = [header, osc_widget]
    pile = urwid.Filler(urwid.Pile(widgets), valign='top')
    return pile


def init_audio_source(video_buffer):
    header = column_header("audio source")
    widgets = [header,]

    def callback(_radio_button, state, device_index):
        if state:
            audio_input.change_stream(device_index)

    radio_group = []
    for device_index, device in enumerate(sounddevice.query_devices()):

        if device['max_input_channels'] < 2:
            continue

        radio = urwid.RadioButton(
            radio_group,
            f"{device['name']}",
            state=device['name'] == audio_input.INPUT_DEVICE_NAME,
            on_state_change=callback,
            user_data=device_index
        )
        widgets.append(radio)

    pile = urwid.Filler(urwid.Pile(widgets), valign='top')
    return pile


def init_fx(video_buffer):
    header = column_header("f/x")
    widgets = [header,]

    def callback(_check_box, state, fx):
        fx.enabled = state

    for label, fx in video_buffer.effects.items():
        check_box = urwid.CheckBox(str(fx), state=fx.enabled)
        user_data = fx
        urwid.connect_signal(check_box, 'change', callback, user_data)

        widgets.append(check_box)
    pile = urwid.Filler(urwid.Pile(widgets), valign='top')
    return pile


def init_logs():
    header = column_header("logs")
    widgets = [header,listbox]
    pile = urwid.Filler(urwid.Pile(widgets), valign='top')
    return pile


async def update_ui(video_buffer):

    global SLEEP_TIME

    while True:
        await asyncio.sleep(SLEEP_TIME)
        if not video_buffer.enabled:
            continue

        for param in params_widgets:
            widget, options = param.contents[1]
            text = param.update_function()
            widget.set_text(text)

        if pixel_check_box.get_state():
            SLEEP_TIME = 0.05
            await update_pixels(video_buffer)
        else:
            SLEEP_TIME = 0.5


async def osc_handler():
    keys = {}

    def make_key(osc):
        address = osc[0]
        if address == "/midi/note":
            channel = str(osc[3])
            key = address + channel
        elif address ==  "/midi/cc":
            channel = str(osc[1])
            key = address + channel
        else:
            key = address
        return key

    while True:
        osc = await osc_queue.get()
        key = make_key(osc)
        message = "{}".format(osc)

        if key in keys:
            i = keys[key]
            widget, options = osc_widget.contents[i]
            widget.set_text(message)
        else:
            i = len(osc_widget.contents)
            options = ('weight', 1)
            new = urwid.Text(('header', message), align='left')
            osc_widget.contents.append((new, options))
            keys[key] = i


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
    audio = init_audio_source(video_buffer)
    fx = init_fx(video_buffer)
    osc = init_osc()

    body = urwid.Columns((
        ('weight', 1, params),
        ('weight', 1, osc),
        ('weight', 1, audio),
        ('weight', 1, fx),
        ('weight', 1, listbox),
    ), dividechars=3)

    frame = urwid.Frame(body, header=header, footer=footer)
    return frame


def input_handler(key):

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
    if osc_queue:
        osc_queue.put_nowait(args)


def init(loop, video_buffer):
    global _video_buffer
    global osc_queue
    osc_queue = asyncio.Queue(loop=loop)
    _video_buffer = video_buffer

    global urwid_loop
    event_loop = urwid.AsyncioEventLoop(loop=loop)
    # slow down refresh
    event_loop._idle_emulation_delay = 1/10 # 1/18
    main_widget = urwid_console(video_buffer)
    urwid_loop = urwid.MainLoop(main_widget, palette, event_loop=event_loop, unhandled_input=input_handler)
    asyncio.ensure_future(log_handler())
    asyncio.ensure_future(osc_handler())
    asyncio.ensure_future(update_ui(video_buffer))
    urwid_loop.start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    from video_buffer import VideoBuffer

    init(loop, VideoBuffer(N=420))
