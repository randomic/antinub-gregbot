import logging, logging.config
import os, json
import config

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


from importlib import import_module

import discord.ext.commands as commands

# Create the bot
bot = commands.Bot('!')

@bot.listen()
async def on_ready():
    logger.info('Logged in as %s, id: %s', bot.user.name, bot.user.id)


# Import the bot's extensions and initialize them.
logger.info('Loading extensions')

for ext in config.ENABLED_EXTENSIONS:
    try:
        bot.load_extension('ext.%s' % ext)
        logger.info('Successfully loaded extension: %s', ext)
    except ImportError as e:
        logger.warn('Failed to load extension: %s - %s', ext, e)


logger.info('Starting up bot')
bot.run(config.TOKEN)