import logging
import serial

BAUDRATE = 460800
# BAUDRATE = 230400
# BAUDRATE = 115200

# try these in order until one opens
SERIAL_DEVS = (
    '/dev/cu.usbmodem1411',
    '/dev/cu.usbmodem1421',
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
            return s
        except (serial.SerialException, OSError):
            logging.warn("Couldn't open serial port {}".format(dev))
    raise Exception("couldn't open any serial port, failing")

def reset_to_top(serial_f):
    arduino_status = 1  # 0 indicates ready for entire frame
    i=0
    while arduino_status != 0:
        if serial_f.inWaiting() > 0:
            arduino_status = ord(serial_f.read())
            i+=1
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
    except:
        logging.warn("no serial")
