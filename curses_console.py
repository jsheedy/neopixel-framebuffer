import asyncio
import json
import logging

import urwid

import log


logger = logging.getLogger()

attrs_txt = urwid.Text("ATTRS HERE")

palette = [
    ('header', 'black', 'light blue'),
    ('footer', 'black', 'light green'),
    ('columnheader', 'black', 'light gray'),
    ('paused', 'light red', 'white'),
    ('playing', 'dark green', 'black'),
]

parameters = [
    ('param 1', '0', lambda: "goat"),
    ('param 2', '0', lambda: "-0"),
]

play_pause_indicator = urwid.Text('PLAYING', align='center', wrap='clip')
play_pause_indicator_attr = urwid.AttrWrap(urwid.Padding(play_pause_indicator), 'playing')

_video_buffer = None
game_state = urwid.Text('', align='left')

params_widgets = []

urwid_loop = None

lw = urwid.SimpleListWalker([])
listbox = urwid.ListBox(lw)
listbox = urwid.AttrWrap(listbox, 'listbox')

pixels = []

def update_pixels(video_buffer):

    foreground = "#fff"
    colors = 256
    for i, pixel in enumerate(pixels):
        r,g,b = video_buffer.buffer[i*3:i*3+3]
        entry = "#" + "".join(["{:02x}".format(x)[0] for x in (r,g,b)])
        attr = urwid.AttrSpec(foreground, entry, colors)
        pixel.set_attr_map({None: attr})


def init_params(video_buffer):

    parameters = (
        ("frame", "0", lambda: str(video_buffer.frame)),
    )

    for label, value, update_function in parameters:

        widget = urwid.Columns([
            urwid.Text(label, align='left'),
            urwid.Text(value, align='right'),
        ])
        widget.update_function = update_function


    params_widgets.append(widget)

    divider = urwid.Divider('-')
    widgets = [urwid.Padding(play_pause_indicator_attr), divider] + params_widgets + [divider, game_state]

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


def init_plays(video_buffer):
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
        await asyncio.sleep(0.1)


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
    plays = init_plays(video_buffer)
    logs = init_logs()

    body = urwid.Columns((
        ('weight', 1, params),
        ('weight', 1, plays),
        ('weight', 1, logs),
    ), dividechars=3)

    frame = urwid.Frame(body, header=header, footer=footer)
    return frame


def clear():
    lw[:] = []
    last_play.set_text('')

    for param in params_widgets:
        widget, options = param.contents[1]
        widget.set_text('')

    game_state.set_text('')


def show_or_exit(key):

    if key in ('p', 'P'):
        _video_buffer.enabled = not _video_buffer.enabled
        msg = _video_buffer.enabled and "PLAYING" or "PAUSED"
        logger.info(msg)
        play_pause_indicator.set_text(msg)
        play_pause_indicator_attr.set_attr(msg.lower())

    elif key in ('c', 'C'):
        clear()

    elif key in ('q', 'Q'):
        for task in asyncio.Task.all_tasks():
            task.cancel()
        urwid_loop.stop()
        asyncio.get_event_loop().stop()


def console(loop, video_buffer):
    colors = 256
    global _video_buffer
    _video_buffer = video_buffer
    asyncio.ensure_future(log_handler())
    asyncio.ensure_future(update_ui(video_buffer))
    global urwid_loop
    urwid_loop = urwid.MainLoop(urwid_console(video_buffer), palette, event_loop=urwid.AsyncioEventLoop(), unhandled_input=show_or_exit)
    screen = urwid_loop.screen
    screen.set_terminal_properties(colors)
    urwid_loop.start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    from video_buffer import VideoBuffer

    console(loop, VideoBuffer(N=420))
