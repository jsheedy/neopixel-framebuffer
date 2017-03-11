from asyncio import Queue
import logging
from logging.handlers import QueueHandler


queue = Queue()


def configure_logging(level=None, detailed=True, color=False):

    if detailed:
        fmt = '[%(asctime)s (%(relativeCreated)dms) PID %(process)d] [%(pathname)s:%(lineno)d/%(funcName)s] %(levelname)s - %(message)s'
    else:
        fmt = '%(pathname)s:%(lineno)d %(levelname)s - %(message)s'

    kwargs = {
        'level': (level or logging.INFO),
        'datefmt': '%Y-%m-%d %H:%M:%S',
        'format': fmt
    }
    logging.basicConfig(**kwargs)
    logger = logging.getLogger()
    logger.handlers = []
    logger.addHandler(QueueHandler(queue))

