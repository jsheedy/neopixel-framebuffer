import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt

CHUNK = 2048
WIDTH = 2
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 6.4

p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=4, # Soundflower input
                output_device_index=3, # Saffire output
                output=True,
                frames_per_buffer=CHUNK)

while True:
    data = stream.read(CHUNK)
    a = np.fromstring(data, dtype=np.int16)

    r_channel = a[1:-1:2]
    l_channel = a[0:-1:2]

    print(data)
    # stream.write(a.tobytes(), CHUNK)

stream.stop_stream()
stream.close()

p.terminate()