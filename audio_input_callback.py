import logging

import pyaudio
import numpy as np
from pythonosc import osc_message_builder

import websocket_server

CHUNK = 512
WIDTH = 2
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 6.4

p = pyaudio.PyAudio()

video_buffer = None

def send_osc(fft_array):
    if not fft_array.any():
        loggging.info("received bad fft_array")
        return
    try:
        msg = osc_message_builder.OscMessageBuilder(address = "/fft")
        msg.add_arg(fft_array.tolist())
        msg = msg.build()
        websocket_server.osc_recv(msg)
    except:
        print("no OSC send from audio_input_callback")

def callback(data, frame_count, time_info, status):
    # read from static file
    # data = wf.readframes(frame_count)

    # print("{} {} {} {}".format(len(data), frame_count, time_info, status))
    # 4096 1024 {'output_buffer_dac_time': 8951.970791577092, 'current_time': 8951.946201123, 'input_buffer_adc_time': 8951.902696622441} 0

    a = np.fromstring(data, dtype=np.int16)
    r_channel = a[1::2]
    l_channel = a[0:-1:2]

    mono = np.empty(shape=(frame_count,), dtype=np.int16)
    mono[:] = r_channel / 2 + l_channel / 2

    window = np.hanning(frame_count)
    fft = np.fft.fft(mono * window)

    try:
        db_fft = np.abs(fft[1:CHUNK/2])**2
        db_fft = 20*np.log10(db_fft)
    except:
        print("fft broke")
        return

    # min, max = np.clip(np.min(db_fft), 0,200), np.clip(np.max(db_fft), 0, 200)
    # print("{} / {} / {}".format(min, max, len(db_fft)))
    # stretched_fft = np.clip((db_fft - min - 20) / (max-min) * 255, 0, 255)
    # fft_uint8 = np.clip(db_fft-50,0, 255).astype(np.uint8)
    # fft_uint8 = (stretched_fft[:video_buffer.N]).astype(np.uint8)

    n_octaves = 4
    f0 = 55
    note_frequencies = [f0*(2**(1/12))**x for x in range(0,12*n_octaves+1)]
    # len 49
    frequencies = np.linspace(0, RATE/2.0, frame_count)
    # interpolated = np.interp(note_frequencies, frequencies, db_fft)
    interpolated = db_fft[:100]

    l = len(interpolated)

    send_osc(interpolated)
    video_buffer.buffer[0:l*3:3] = interpolated[:] # fft_uint8[:100]
    # vb range: 0-420
    # fft range: 0-20000
    # first [:100] of fft_range goes to 4.271khz
    # [:420] goes to 18.080khz
    # linterp [:100] to [:420]

    # for i,f in enumerate(note_frequencies[:-2]):
    #     print("{}: {} : {}".format(i, f, interpolated[i]))
    # print("----")

    # import ipdb;ipdb.set_trace()
    # swallow audio
    # return

    return (data, pyaudio.paContinue)

def input_audio_stream(vb):

    global video_buffer
    video_buffer = vb

    stream = p.open(format=p.get_format_from_width(WIDTH),
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=4, # Soundflower input
                    # output_device_index=3, # Saffire output
                    # output_device_index=4, # Soundflower output 2
                    output_device_index=5, # Soundflower output 64
                    output=True,
                    frames_per_buffer=CHUNK,
                    stream_callback=callback)

    stream.start_stream()

# stream.stop_stream()
# stream.close()
#
# p.terminate()
