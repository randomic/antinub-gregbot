'''
Entry point for antinub-gregbot project.

Configures logging, loads startup extensions and starts the bot.
'''
import logging

import discord.ext.commands as commands
from tinydb import TinyDB

from utils.log import configure_logging
from utils.config import Config


def start_bot():
    """Attempt to load required config or ask user (generally first time).

    """
    tdb = TinyDB('db.json')
    config = Config(tdb)

    debug = config.get('debug')
    if not debug:
        debug = False
        config.set('debug', debug)
    logging.getLogger().setLevel(logging.DEBUG if debug else logging.INFO)

    cmd_prefixes = config.get('cmd_prefixes')
    if not cmd_prefixes:
        cmd_prefixes = []
        config.set('cmd_prefixes', cmd_prefixes)

    token = config.get('token')
    if not token:
        token = input('Enter token: ')
        save_token = (config, token)
    else:
        save_token = None

    owner_id = config.get('owner_id')
    if not owner_id:
        owner_id = input('Enter owner ID: ')
        config.set('owner_id', owner_id)

    bot = commands.Bot(commands.when_mentioned_or(*cmd_prefixes),
                       pm_help=True)
    bot.loop.create_task(when_ready(bot, save_token))
    bot.tdb = tdb
    bot.config = config

    bot.run(token)


async def when_ready(bot, save_token=None):
    """Wait until the bot is ready, then load extensions.

    """
    await bot.wait_until_ready()
    logger = logging.getLogger(__name__)
    logger.info('Logged in as %s, id: %s', bot.user.name, bot.user.id)
    if save_token:
        # If a token was given during startup, save it now we know it's valid.
        config, token = save_token
        config.set('token', token)
    load_extensions(bot)


def load_extensions(bot):
    'Load the startup extensions'
    logger = logging.getLogger(__name__)
    logger.info('Loading core extensions')
    bot.load_extension('core')
    logger.info('Successfully loaded core extensions')

    loaded_extensions = bot.config.get('loaded_extensions')
    if not loaded_extensions:
        loaded_extensions = []
        bot.config.set('loaded_extensions', loaded_extensions)

    for ext in loaded_extensions:
        ext_mod = 'ext.{}'.format(ext)
        if ext_mod not in bot.extensions:
            try:
                bot.load_extension(ext_mod)
                logger.info('Successfully loaded extension: %s', ext)
            except ImportError as error:
                logger.warning(
                    'Failed to load extension: %s - %s', ext, error)
        else:
            logger.warning('Extension with same name already loaded: %s', ext)


if __name__ == '__main__':
    configure_logging()
    start_bot()
