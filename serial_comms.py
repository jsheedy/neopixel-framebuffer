import logging
import serial

# BAUDRATE = 9600
BAUDRATE = 460800
# BAUDRATE = 230400
# BAUDRATE = 115200

# try these in order until one opens
SERIAL_DEVS = (
    '/dev/tty.usbmodem1451',
    '/dev/tty.usbmodemfd141',
    '/dev/tty.usbmodem1411',
    '/dev/tty.usbmodemfd131',
    '/dev/tty.usbmodemfa141',
)

video_frame = 0
serial_f = None

def open_serial():
    for dev in SERIAL_DEVS:
        try:
            s = serial.Serial(port=dev, baudrate=BAUDRATE, timeout=2)
            logging.info("Opened serial port {}".format(dev))
            # flush buffers
            # while(s.inWaiting() == 0):
            #     s.write(0)

            return s
        except (serial.SerialException, OSError):
            logging.warn("Couldn't open serial port {}".format(dev))
    raise Exception("couldn't open any serial port, failing")

def write_serial(serial_f, video_buffer):
    global video_frame
    serial_f.read(serial_f.inWaiting())
    if video_buffer.frame > video_frame:
        logging.debug('serial reserving frame {}'.format(video_buffer.frame))
        video_frame = video_buffer.frame
    else:
        video_frame = video_buffer.update()

    serial_f.write(video_buffer.buffer.tobytes())

def init(loop, video_buffer):
    global serial_f
    try:
        serial_f = open_serial()
        loop.add_reader(serial_f.fileno(), write_serial, serial_f, video_buffer)
    except:
        logging.warn("no serial")
