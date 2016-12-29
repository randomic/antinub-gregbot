'''
Entry point for antinub-gregbot project.

Configures logging, loads startup extensions and starts the bot.
'''
import logging
from logging.handlers import RotatingFileHandler
from socket import AF_INET
import os

from aiohttp import TCPConnector
import discord.ext.commands as commands

import config


def _configure_logging():
    'Adds file and console handlers and formats the root logger'
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if config.DEBUG else logging.INFO)

    fmt = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_dh = RotatingFileHandler(
        os.path.join(config.LOG_PATH, 'debug.log'),
        maxBytes=1000000,
        backupCount=5,
        encoding='utf-8')
    file_dh.setLevel(logging.DEBUG)
    file_dh.setFormatter(fmt)
    file_dh.doRollover()
    root_logger.addHandler(file_dh)

    file_ih = RotatingFileHandler(
        os.path.join(config.LOG_PATH, 'info.log'),
        maxBytes=1000000,
        backupCount=5,
        encoding='utf-8')
    file_ih.setLevel(logging.INFO)
    file_ih.setFormatter(fmt)
    file_ih.doRollover()
    root_logger.addHandler(file_ih)

    file_eh = RotatingFileHandler(
        os.path.join(config.LOG_PATH, 'error.log'),
        maxBytes=100000,
        backupCount=5,
        encoding='utf-8')
    file_eh.setLevel(logging.ERROR)
    file_eh.setFormatter(fmt)
    file_eh.doRollover()
    root_logger.addHandler(file_eh)

    console_h = logging.StreamHandler()
    console_h.setLevel(logging.DEBUG)
    console_h.setFormatter(fmt)
    root_logger.addHandler(console_h)


def _load_extensions(bot):
    'Load the startup extensions'
    logger = logging.getLogger(__name__)
    logger.info('Loading extensions')
    bot.load_extension('utils.control')
    logger.info('Successfully loaded extension: control')

    for ext in config.STARTUP_EXTENSIONS:
        ext_string = 'ext.{}'.format(ext)
        if ext_string not in bot.extensions:
            try:
                bot.load_extension(ext_string)
                logger.info('Successfully loaded extension: %s', ext)
            except ImportError as exc:
                logger.warning('Failed to load extension: %s - %s', ext, exc)
        else:
            logger.warning('Extension with same name already loaded: %s', ext)


if __name__ == '__main__':
    _configure_logging()
    LOGGER = logging.getLogger(__name__)
    LOGGER.info('Starting up bot')
    CONNECTOR = TCPConnector(family=AF_INET if config.FORCE_IPV4 else 0)
    BOT = commands.Bot(commands.when_mentioned_or(*config.COMMAND_PREFIXES),
                       pm_help=True,
                       connector=CONNECTOR)

    @BOT.listen()
    async def on_ready():
        'Note in log when the bot is ready'
        LOGGER.info('Logged in as %s, id: %s', BOT.user.name, BOT.user.id)
        _load_extensions(BOT)

    BOT.run(config.TOKEN)
