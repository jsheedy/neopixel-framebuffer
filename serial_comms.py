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
    'loop': None,
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
    i = 0
    try:
        while arduino_status != 0:
            if serial_f.inWaiting() > 0:
                arduino_status = ord(serial_f.read())
                logger.debug(f'arduino_status: {arduino_status}')
                i += 1
            else:
                # dump 3 bytes to fill the input buffer
                logger.debug(f'writing 3 0 bytes')
                serial_f.write(bytes((0,)*3))
    except Exception as e:
        logger.exception(e)
        init(globals['loop'], globals['video_buffer'])


def write_serial():
    serial_f = globals['serial_f']
    video_buffer = globals['video_buffer']

    reset_to_top(serial_f)

    if video_buffer.frame > globals['video_frame']:
        logging.debug('serial reserving frame {}'.format(video_buffer.frame))
        globals['video_frame'] = video_buffer.frame
    else:
        logging.debug('updating on frame {}'.format(video_buffer.frame))
        globals['video_frame'] = video_buffer.update()

    data = video_buffer.buffer.tobytes()
    globals['serial_f'].write(data)

def bootup_sequence():
    write_serial()

def init(loop, video_buffer):
    globals['video_buffer'] = video_buffer
    globals['loop'] = loop
    try:
        globals['serial_f'] = open_serial()
        bootup_sequence()
        loop.add_reader(globals['serial_f'].fileno(), write_serial)
    except SerialPortError:
        logger.critical("\n\nCOULD NOT OPEN SERIAL PORT\n\n")
