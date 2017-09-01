'''
Entry point for antinub-gregbot project.

Configures logging, loads startup extensions and starts the bot.
'''
import logging

import discord.ext.commands as commands
from tinydb import TinyDB, Query

from utils.log import configure_logging


def start_bot():
    """Attempt to load required config or ask user (generally first time).

    """
    table = TinyDB('db.json').table('config')
    setting = Query()

    debug = table.get(setting.name == 'debug')
    if debug:
        debug = debug['value']
    else:
        debug = False
        table.insert({'name': 'debug', 'value': debug})
    logging.getLogger().setLevel(logging.DEBUG if debug else logging.INFO)

    cmd_prefixes = table.get(setting.name == 'cmd_prefixes')
    if cmd_prefixes:
        cmd_prefixes = cmd_prefixes['value']
    else:
        cmd_prefixes = []
        table.insert({'name': 'cmd_prefixes', 'value': cmd_prefixes})

    token = table.get(setting.name == 'token')
    if token:
        token = token['value']
        save_token = None
    else:
        token = input('Enter token: ')
        save_token = (table, token)

    bot = commands.Bot(commands.when_mentioned_or(*cmd_prefixes),
                       pm_help=True)
    bot.loop.create_task(when_ready(bot, save_token))

    bot.run(token)


async def when_ready(bot, save_token=None):
    """Wait until the bot is ready, then load extensions.

    """
    await bot.wait_until_ready()
    logger = logging.getLogger(__name__)
    logger.info('Logged in as %s, id: %s', bot.user.name, bot.user.id)
    if save_token:
        table, token = save_token
        table.insert({'name': 'token', 'value': token})
    load_extensions(bot)


def load_extensions(bot):
    'Load the startup extensions'
    logger = logging.getLogger(__name__)
    logger.info('Loading extensions')
    bot.load_extension('utils.control')
    logger.info('Successfully loaded extension: control')

    for ext in []:
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
    configure_logging()
    start_bot()
