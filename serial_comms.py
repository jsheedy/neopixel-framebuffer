import asyncio
import glob
import logging

import serial

logger = logging.getLogger(__name__)

BAUDRATE = 460800
# BAUDRATE = 230400
# BAUDRATE = 115200

SERIAL_DEVICE_PATTERN = '/dev/*.usbmodem*'

globals = {
    'serial_f': None,
    'video_buffer': None,
    'video_frame': 0
}

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
    try:
        while arduino_status != 0:
            if serial_f.inWaiting() > 0:
                arduino_status = ord(serial_f.read())
            else:
                serial_f.write(bytes((0,)))
                logger.info('byte')

    except Exception as e:
        logger.exception(e)
        init(globals['video_buffer'])


def write_serial():
    serial_f = globals['serial_f']
    video_buffer = globals['video_buffer']
    reset_to_top(serial_f)
    serial_f.write(video_buffer.uint8)


def init(video_buffer):
    loop = asyncio.get_event_loop()
    globals['video_buffer'] = video_buffer
    try:
        globals['serial_f'] = open_serial()
        loop.add_reader(globals['serial_f'].fileno(), write_serial)
    except SerialPortError:
        logger.critical("\n\nCOULD NOT OPEN SERIAL PORT\n\n")
