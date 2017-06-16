import pyaudio
import numpy as np
from pythonosc import osc_message_builder
import sounddevice

import websocket_server

CHUNK = 2048
WIDTH = 2
CHANNELS = 2
RATE = 44100

INPUT_DEVICE_NAME = 'Loopback Audio'
OUTPUT_DEVICE_INDEX = 3  # soundflower 64 output

pa = pyaudio.PyAudio()

video_buffer = None


def send_osc(fft_array):
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
        peak_meter.envelope('', h, i, gain=2.0)

    return (data, pyaudio.paContinue)


def input_audio_stream(callback):
    input_device_index = next((i for i,x in enumerate(sounddevice.query_devices()) if x['name'] == INPUT_DEVICE_NAME))
    stream = pa.open(
        format=pa.get_format_from_width(WIDTH),
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=input_device_index,
        output_device_index=OUTPUT_DEVICE_INDEX,
        output=True,
        frames_per_buffer=CHUNK,
        stream_callback=callback
    )

    stream.start_stream()


if __name__ == "__main__":
    input_audio_stream(print)
    input()
