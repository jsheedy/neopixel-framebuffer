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
wf = wave.open('./sagan_ask_the_next_question.wav', 'rb')

print("* recording")

# for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
# while True:
fig, ax = plt.subplots()  #create figure and axes
ax.set_ylim(0,130)

f = np.linspace(0, RATE/2.0, CHUNK/2)
plt.xlabel("Frequency(Hz)")
plt.ylabel("Power(dB)")
plt.show(block=False)
input('go')
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):

    # from audio device
    # data = stream.read(CHUNK)
    # import ipdb;ipdb.set_trace()
    # ax.clear()

    data = wf.readframes(CHUNK)
    a = np.fromstring(data, dtype=np.int16)

    r_channel = a[1:-1:2]
    fft = np.fft.fft(r_channel)

    # show waveform
    # import ipdb;ipdb.set_trace()
    # t = np.arange(len(r_channel))*1.0/RATE
    # plt.plot(t, r_channel)
    # plt.show()

    # plot fft
    # p = 20*np.log10(np.abs(np.fft.rfft(r_channel)))
    # ax.plot(f, p, scaley=False)
    # plt.pause(0.000000001)

    stream.write(a.tobytes(), CHUNK)


print("* done")

stream.stop_stream()
stream.close()

p.terminate()