import glob
import logging

import serial

logger = logging.getLogger(__name__)

BAUDRATE = 460800
# BAUDRATE = 230400
# BAUDRATE = 115200

SERIAL_DEVICE_PATTERN = '/dev/*.usbmodem*'

video_frame = 0
serial_f = None


class SerialPortError(Exception): pass


def open_serial():
    for dev in glob.glob(SERIAL_DEVICE_PATTERN):
        try:
            s = serial.Serial(port=dev, baudrate=BAUDRATE, timeout=2)
            logging.info("Opened serial port {}".format(dev))
            return s
        except (serial.SerialException, OSError):
            logging.warn("Couldn't open serial port {}".format(dev))

    raise SerialPortError

def reset_to_top(serial_f):
    arduino_status = 1  # 0 indicates ready for entire frame
    i = 0
    while arduino_status != 0:
        if serial_f.inWaiting() > 0:
            arduino_status = ord(serial_f.read())
            i += 1
        else:
            # dump 3 bytes to fill the input buffer
            serial_f.write(bytes((0,)*3))


def write_serial(serial_f, video_buffer):
    global video_frame

    reset_to_top(serial_f)

    if video_buffer.frame > video_frame:
        logging.debug('serial reserving frame {}'.format(video_buffer.frame))
        video_frame = video_buffer.frame
    else:
        video_frame = video_buffer.update()

    data = video_buffer.buffer.tobytes()
    serial_f.write(data)


def init(loop, video_buffer):
    global serial_f
    try:
        serial_f = open_serial()
        loop.add_reader(serial_f.fileno(), write_serial, serial_f, video_buffer)
    except SerialPortError:
        logger.critical("\n\nCOULD NOT OPEN SERIAL PORT\n\n")
