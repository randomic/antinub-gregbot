'''
Module containing default logging settings for gregbot.
'''
import logging
import logging.config

from discord.ext import commands

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(levelname)8s - %(name)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/error.log',
            'backupCount': 5,
            'maxBytes': 1048576,
            'encoding': 'utf-8',
            'formatter': 'default',
        },
    },
    'root': {
        'handlers': ['console', 'error'],
        'level': 'WARNING',
    },
}


def get_logger(name: str, debug: bool):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    return logger


def configure_logging():
    """Load the default config and rollover any rotating file handlers.

    """
    logging.config.dictConfig(DEFAULT_LOGGING)
    logging.captureWarnings(True)

    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.handlers.RotatingFileHandler):
            handler.doRollover()
