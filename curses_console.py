import asyncio
import functools
import logging
import operator
import time

import sounddevice
import urwid

import audio_input
from exceptions import UserQuit
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

colors = 256
params_widgets = []
pixel_check_box = None
pixels = []

urwid_loop = None

SLEEP_TIME = 0.25
fullscreen = False
lw = urwid.SimpleFocusListWalker([])
# lw = urwid.SimpleListWalker([])
listbox = urwid.ListBox(lw)
listbox = urwid.AttrWrap(listbox, 'listbox')

osc_widget = None

video_buffer = None

t0 = time.time()
f0 = 0

@functools.lru_cache()
def get_attr(rgb):
    """ caches AttrSpecs """
    foreground = "#fff"
    colors = 256
    entry = "#" + "".join(["{:02x}".format(x)[0] for x in rgb])
    return {None: urwid.AttrSpec(foreground, entry, colors)}


async def update_pixels():
    buffer = video_buffer.uint8
    for i, pixel in enumerate(pixels):
        rgb = tuple(buffer[i*3:i*3+3])
        attr = get_attr(rgb)
        pixel.set_attr_map(attr)


def init_params():
    def fps():
        global t0
        global f0
        t1 = time.time()
        f1 = video_buffer.frame
        dt = t1-t0
        df = f1 - f0
        t0 = t1
        f0 = f1
        return "{:.1f} fps".format(df/dt)

    def runtime():
        return "{:.1f}s".format(video_buffer.t)

    parameters = (
        ("frame", "0", lambda: str(video_buffer.frame)),
        ("fps", "0", fps),
        ("runtime", "0", runtime)
    )
    params_widgets.clear()
    for label, value, update_function in parameters:

        widget = urwid.Columns([
            urwid.Text(label, align='left'),
            urwid.Text(value, align='right'),
        ])
        widget.update_function = update_function
        params_widgets.append(widget)

    divider = urwid.Divider('-')

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
    if osc_widget is None:
        osc_widget = urwid.Pile([text_widget])
    widgets = [header, osc_widget]
    pile = urwid.Filler(urwid.Pile(widgets), valign='top')
    return pile


def init_audio_source():
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

def init_operator():
    header = column_header("operator")
    group = []

    def callback(_radio_button, state, operator):
        if state:
            video_buffer.operator = operator
            logging.warning(operator)

    ops = (
        ('+', operator.add),
        ('-', operator.sub),
        ('*', operator.mul),
        ('/', operator.truediv),
        ('**', operator.pow),
    )
    widgets = [header]
    for label,op in ops:
        button = urwid.RadioButton(group, label, state=(op == video_buffer.operator), on_state_change=callback, user_data=op)
        widgets.append(button)

    component = urwid.Pile(widgets)

    return component


def init_fx():
    fx_header = column_header("f/x")
    operator = init_operator()
    widgets = [operator, fx_header,]

    def callback(_check_box, state, fx):
        fx.enabled = state

    def text_callback(widget, value, user_data):
        # raise Exception(value)
        # console.warning(value)
        # console.warning(user_data)
        fx = user_data['fx']
        logging.warning(fx)
        fx.parameters[user_data['key']] = int(value)

    for label, fx in video_buffer.effects.items():
        check_box = urwid.CheckBox(str(fx), state=fx.enabled)
        user_data = fx
        urwid.connect_signal(check_box, 'change', callback, user_data)

        widgets.append(check_box)

        for key, param in fx.parameters.items():
            widget = urwid.Edit(caption=key, edit_text=str(param))
            user_data = {'key': key, 'fx': fx}
            urwid.connect_signal(widget, 'change', text_callback, user_data)
            widgets.append(widget)

    pile = urwid.Filler(urwid.Pile(widgets), valign='top')
    return pile


def init_logs():
    header = column_header("logs")
    widgets = [header,listbox]
    pile = urwid.Filler(urwid.Pile(widgets), valign='top')
    return pile


async def update_ui():

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
            SLEEP_TIME = 0.03
            await update_pixels()
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
        listbox.set_focus(len(lw) - 1, 'above')
        # clear old
        if len(lw) > 30:
            lw.pop(0)


def urwid_console():

    header = urwid.Text("NEOPIXEL FRAMEBUFFER", align='center')
    header = urwid.AttrWrap(header, 'header')

    footer = urwid.Text("keys: (q)uit, (p)ause/resume, (f)ullscreen")
    footer = urwid.AttrWrap(footer, 'footer')

    params = init_params()
    audio = init_audio_source()
    fx = init_fx()
    osc = init_osc()

    audio_osc = urwid.Pile([audio, osc, listbox])

    body = urwid.Columns((
        ('weight', 1, params),
        ('weight', 1, fx),
        ('weight', 1, audio_osc),
    ), dividechars=3)

    frame = urwid.Frame(body, header=header, footer=footer)
    return frame


def stop():
    urwid_loop.stop()
    # raise urwid.ExitMainLoop


def input_handler(key):
    global urwid_loop

    if key in ('p', 'P'):
        video_buffer.enabled = not video_buffer.enabled
        msg = video_buffer.enabled and "PLAYING" or "PAUSED"
        logger.info(msg)
        play_pause_indicator.set_text(msg)
        play_pause_indicator_attr.set_attr(msg.lower())

    elif key in ('q', 'Q'):
        urwid_loop.stop()
        for t in asyncio.Task.all_tasks():
            t.cancel()

    elif key in ('f', 'F'):
        global fullscreen
        fullscreen = not fullscreen
        if fullscreen:
            grid_flow = urwid.GridFlow(pixels, 3, 0, 0, 'center')
            urwid_loop.widget = urwid.Filler(grid_flow)
        else:
            urwid_loop.widget = urwid_console()


def osc_recv(*args):
    if osc_queue:
        osc_queue.put_nowait(args)


def init(_video_buffer):
    global video_buffer
    global osc_queue
    global urwid_loop

    osc_queue = asyncio.Queue()
    video_buffer = _video_buffer

    for i in range(video_buffer.N):
        attr = get_attr((0,0,0))
        text = urwid.Text("")
        pixel = urwid.AttrMap(text, attr)
        pixels.append(pixel)

    loop = asyncio.get_event_loop()
    event_loop = urwid.AsyncioEventLoop(loop=loop)
    # slow down refresh
    event_loop._idle_emulation_delay = 1/10 # 1/18
    main_widget = urwid_console()
    urwid_loop = urwid.MainLoop(
        main_widget,
        palette,
        event_loop=event_loop,
        unhandled_input=input_handler)
    urwid_loop.start()
    return (log_handler(), osc_handler(), update_ui())
