'''
Entry point for antinub-gregbot project.

Configures logging, loads startup extensions and starts the bot.
'''
import logging
from logging.handlers import RotatingFileHandler
import os

import discord.ext.commands as commands

import config


def _configure_logging():
    'Adds file and console handlers and formats the root logger'
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if config.DEBUG else logging.INFO)

    fmt = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_h = RotatingFileHandler(
        os.path.join(config.LOG_PATH, 'info.log'))
    file_h.setLevel(logging.INFO)
    file_h.setFormatter(fmt)
    root_logger.addHandler(file_h)

    console_h = logging.StreamHandler()
    console_h.setLevel(logging.DEBUG)
    console_h.setFormatter(fmt)
    root_logger.addHandler(console_h)


def _load_extensions(bot):
    'Load the startup extensions'
    logger = logging.getLogger(__name__)
    logger.info('Loading extensions')

    for ext in config.STARTUP_EXTENSIONS:
        try:
            bot.load_extension('ext.%s' % ext)
            logger.info('Successfully loaded extension: %s', ext)
        except ImportError as exc:
            logger.warning('Failed to load extension: %s - %s', ext, exc)


if __name__ == '__main__':
    _configure_logging()

    # Create the bot
    LOGGER = logging.getLogger(__name__)
    LOGGER.info('------------------------------')
    LOGGER.info('Starting up bot')
    BOT = commands.Bot('!')
    _load_extensions(BOT)

    @BOT.listen()
    async def on_ready():
        'Note in log when the bot is ready'
        LOGGER.info('Logged in as %s, id: %s', BOT.user.name, BOT.user.id)

    BOT.run(config.TOKEN)
