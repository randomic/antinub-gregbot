'''
Entry point for antinub-gregbot project.

Configures logging, loads startup extensions and starts the bot.
'''
import logging
import sys

import discord.ext.commands as commands
from tinydb import TinyDB

from utils.kvtable import KeyValueTable
from utils.log import configure_logging, get_logger


def start_bot():
    """Attempt to load required config or ask user (generally first time).

    """
    tdb = TinyDB('db.json')
    config = KeyValueTable(tdb, 'config')

    try:
        config['debug']
    except KeyError:
        config['debug'] = False

    try:
        cmd_prefixes = config['cmd_prefixes']
    except KeyError:
        cmd_prefixes = []
        config['cmd_prefixes'] = cmd_prefixes

    save_token = False
    try:
        token = config['token']
    except KeyError:
        token = input('Enter token: ')
        save_token = (config, token)

    try:
        owner_id = config['owner_id']
    except KeyError:
        owner_id = input('Enter owner ID: ')
        config['owner_id'] = owner_id

    bot = commands.Bot(when_mentioned_or(*cmd_prefixes), pm_help=True)
    bot.loop.create_task(when_ready(bot, save_token))
    bot.tdb = tdb
    bot.config = config

    bot.run(token)


def when_mentioned_or(*prefixes):
    def inner(bot, msg):
        r = list(prefixes)
        r.append("{0.user.mention} ".format(bot))
        return r

    return inner


async def when_ready(bot, save_token=None):
    """Wait until the bot is ready, then load extensions.

    """
    await bot.wait_until_ready()
    logger = get_logger(__name__, bot)
    logger.info('Logged in as %s, id: %s', bot.user.name, bot.user.id)
    if save_token:
        # If a token was given during startup, save it now we know it's valid.
        config, token = save_token
        config['token'] = token
    load_extensions(bot)


def load_extensions(bot):
    'Load the startup extensions'
    logger = get_logger(__name__, bot)
    logger.info('Loading core extensions')
    bot.load_extension('core')
    logger.info('Successfully loaded core extensions')

    loaded_extensions = bot.config.get('loaded_extensions', [])

    for ext in loaded_extensions.copy():
        ext_mod = 'ext.{}'.format(ext)
        if ext_mod not in bot.extensions:
            try:
                bot.load_extension(ext_mod)
                logger.info('Successfully loaded extension: %s', ext)
            except Exception as error:
                if ext_mod in sys.modules:
                    del sys.modules[ext_mod]
                loaded_extensions.remove(ext)
                logger.exception('Failed to load extension: %s', ext)
        else:
            logger.warning('Extension with same name already loaded: %s', ext)
    bot.config['loaded_extensions'] = loaded_extensions


if __name__ == '__main__':
    configure_logging()
    start_bot()
