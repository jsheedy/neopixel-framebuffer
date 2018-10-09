from asyncio import Queue
import logging
from logging.config import dictConfig
from logging.handlers import QueueHandler

queue = Queue()


def configure_logging(level=logging.INFO, queue_handler=False):

    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '%(pathname)s:%(lineno)d %(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'stream': {
                'class': 'logging.StreamHandler',
                'formatter': 'default'
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'neopixel-framebuffer.log',
                'formatter': 'default'
            },
            'queue': {
                'class': 'logging.handlers.QueueHandler',
                'queue': queue
            }
        },
        'root': {
            'level': level,
            'handlers': (queue_handler and ['queue', 'file','stream'] or ['stream', 'file'])
        }
    })

