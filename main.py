import logging
import logging.config
import os
import json
from importlib import import_module

import config
import discord.ext.commands as commands


# Configure logging from json file or use defaults.
loglevel = logging.DEBUG if config.DEBUG else logging.INFO
path = os.path.join(config.LOG_PATH, 'logging.json')
if os.path.exists(path):
    with open(path, 'rt') as f:
        cfg = json.load(f)
    cfg['root']['level'] = loglevel
    cfg['handlers']['file_handler']['filename'] = os.path.join(config.LOG_PATH, 'info.log')
    logging.config.dictConfig(cfg)
else:
    logging.basicConfig(level=loglevel)

logger = logging.getLogger(__name__)


# Create the client
client = commands.Bot('!')
@client.listen()
async def on_ready():
    logger.info('Logged in as %s, id: %s', client.user.name, client.user.id)


# Import the bot's features and initialize them.
logger.info('Loading features')

for ext in config.ENABLED_EXTENSIONS:
    try:
        client.load_extension('bot.%s' % ext)
    except ImportError as e:
        logger.error('Failed to load extension: %s - %s', ext, e)


logger.info('Starting up bot')
client.run(config.TOKEN)