'''
Entry point for antinub-gregbot project.

Configures logging, loads startup extensions and starts the bot.
'''
import logging
from logging.handlers import RotatingFileHandler
import os
from socket import AF_INET

import discord.ext.commands as commands
from aiohttp import TCPConnector

import config


def _configure_logging():
    'Adds file and console handlers and formats the root logger'
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if config.DEBUG else logging.INFO)

    fmt = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_ih = RotatingFileHandler(
        os.path.join(config.LOG_PATH, 'info.log'))
    file_ih.setLevel(logging.INFO)
    file_ih.setFormatter(fmt)
    root_logger.addHandler(file_ih)

    file_eh = RotatingFileHandler(
        os.path.join(config.LOG_PATH, 'error.log'))
    file_eh.setLevel(logging.ERROR)
    file_eh.setFormatter(fmt)
    root_logger.addHandler(file_eh)

    console_h = logging.StreamHandler()
    console_h.setLevel(logging.DEBUG)
    console_h.setFormatter(fmt)
    root_logger.addHandler(console_h)


def _load_extensions(bot):
    'Load the startup extensions'
    logger = logging.getLogger(__name__)
    logger.info('Loading extensions')
    bot.load_extension('util')
    logger.info('Successfully loaded extension: util')

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


def _create_bot():
    'Create the bot'
    socket_family = AF_INET if config.FORCE_IPV4 else 0
    custom_connector = TCPConnector(family=socket_family)
    return commands.Bot(commands.when_mentioned_or(*config.COMMAND_PREFIXES),
                        pm_help=True,
                        connector=custom_connector)


if __name__ == '__main__':
    _configure_logging()
    LOGGER = logging.getLogger(__name__)
    LOGGER.info('------------------------------')
    LOGGER.info('Starting up bot')
    BOT = _create_bot()

    @BOT.listen()
    async def on_ready():
        'Note in log when the bot is ready'
        LOGGER.info('Logged in as %s, id: %s', BOT.user.name, BOT.user.id)
        _load_extensions(BOT)

    BOT.run(config.TOKEN)
