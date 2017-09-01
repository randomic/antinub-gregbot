'''
Module containing default logging settings for gregbot.
'''
import logging.config


DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'file': {
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
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
    },
}


def configure_logging():
    """Load the default config and rollover any rotating file handlers.

    """
    logging.config.dictConfig(DEFAULT_LOGGING)

    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.handlers.RotatingFileHandler):
            handler.doRollover()
