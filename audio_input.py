import colorsys
import logging

import pyaudio
import numpy as np
from pythonosc import osc_message_builder

from point import Point
import websocket_server

CHUNK = 1024
WIDTH = 2
CHANNELS = 2
RATE = 44100

# INPUT_DEVICE = 3  # Soundflower input
INPUT_DEVICE_INDEX = 3  # Aggregate Audio device nput
# INPUT_DEVICE_INDEX = 6  # Aggregate Audio device nput
OUTPUT_DEVICE_INDEX = 3  # soundflower 64 output

p = pyaudio.PyAudio()

video_buffer = None

def send_osc(fft_array):
    if not fft_array.any():
        loggging.info("received bad fft_array")
        return
    msg = osc_message_builder.OscMessageBuilder(address = "/fft")
    msg.add_arg(fft_array.tolist())
    msg = msg.build()
    websocket_server.osc_recv(msg)


def callback_video_buffer(data, frame_count, time_info, status, video_buffer=None):
    a = np.fromstring(data, dtype=np.int16)
    r_channel = a[1::2]
    l_channel = a[0:-1:2]

    mono = np.empty(shape=(frame_count,), dtype=np.int16)
    mono[:] = r_channel / 2 + l_channel / 2

    # TODO: calculate power spectral density using scipy.signal.periodogram

    h = np.max(mono) / (2**(8*WIDTH))

    peak_meter = video_buffer.effects['peak_meter']
    for i in range(len(peak_meter.meters)):
        peak_meter.envelope('', h, i, gain=4.0)

    a[:] = 0
    return (a.tobytes(), pyaudio.paContinue)


def input_audio_stream(callback):

    # python -m sounddevice to get device list
    # maybe use sounddevice instead
    stream = p.open(format=p.get_format_from_width(WIDTH),
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=INPUT_DEVICE_INDEX,
                    output_device_index=OUTPUT_DEVICE_INDEX,
                    output=True,
                    frames_per_buffer=CHUNK,
                    stream_callback=callback)

    stream.start_stream()

# stream.stop_stream()
# stream.close()
#
# p.terminate()

if __name__ == "__main__":
    from video_buffer import VideoBuffer
    input_audio_stream(print)
    input()