import logging
import logging.config
import os
import json
from importlib import import_module

import config
import discord


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
client = discord.Client()
@client.async_event
def on_ready():
    logger.info('Logged in as %s, id: %s', client.user.name, client.user.id)


# Import the bot's features and initialize them.
logger.info('Loading features')
features = {} # A dictionary to store the instance of the Main class for each feature.

for feature in config.ENABLED_FEATURES:
    module = 'bot.%s' % feature
    try:
        mod = import_module(module)
        main = mod.Main(client)
        features['feature'] = main
        logger.debug('Loaded feature: %s', feature)
    except ImportError as e:
        logger.error('Failed to load feature: %s - %s', feature, e)


logger.info('Starting up bot')
client.run(config.TOKEN)