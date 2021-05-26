'''
Entry point for antinub-gregbot project.

Configures logging, loads startup extensions and starts the bot.
'''
import sys
import os

from pathlib import Path
import yaml
import discord.ext.commands as commands

from utils.log import configure_logging, get_logger


def get_config():
    """
    Load relevant env vars and prepare the config
    """
    conf = {}
    conf['token'] = os.environ.get("GREGBOT_TOKEN")
    conf['owner_id'] = os.environ.get("GREGBOT_OWNER_ID")
    conf['cmd_prefixes'] = os.environ.get("GREGBOT_CMD_PREFIXES").split(',')
    conf['loaded_extensions'] = os.environ.get("GREGBOT_LOADED_EXTENSIONS").split(',')

    return conf

def get_ext_config():
    '''
    Attempts to read the extensions config from either the environment or a file
    '''
    raw_yaml = os.environ.get("GREGBOT_EXT_CONFIG")
    yaml_rel_path = os.environ.get("GREGBOT_EXT_CONFIG_PATH")

    # If ext_config is supplied via an env var, try to parse that.
    if raw_yaml is not None:
        parsed = yaml.load(raw_yaml)
        return parsed

    # If the config was not provided via env var, try reading from file,
    # fallback to 'config.yaml' in the working directory.
    yaml_path = None
    if yaml_rel_path is not None:
        yaml_path = Path(__file__).parent / yaml_rel_path
    else:
        yaml_path = Path(__file__).parent / 'config.yaml'

    if Path.exists(yaml_path):
        with open(yaml_path, 'r') as f:
            parsed = yaml.load(f)
            return parsed

    # If no config is supplied, return None
    return None


def start_bot(conf, ext_conf):
    """Attempt to load required config or ask user (generally first time).

    """
    bot = commands.Bot(when_mentioned_or(conf['cmd_prefixes']), \
        owner_id=conf['owner_id'], pm_help=True)
    bot.loop.create_task(when_ready(bot, conf['loaded_extensions']))
    bot.ext_config = ext_conf
    bot.run(conf['token'])


def when_mentioned_or(prefixes):
    def inner(bot, msg):
        r = prefixes.copy()
        r.append("{0.user.mention} ".format(bot))
        return r

    return inner


async def when_ready(bot, ext_list):
    """Wait until the bot is ready, then load extensions.

    """
    await bot.wait_until_ready()
    logger = get_logger(__name__)
    logger.info('Logged in as %s, id: %s', bot.user.name, bot.user.id)
    load_extensions(bot, ext_list)


def load_extensions(bot, ext_list):
    'Load the startup extensions'
    logger = get_logger(__name__)
    logger.info('Loading core extensions')
    bot.load_extension('core')
    logger.info('Successfully loaded core extensions')

    loaded_extensions = ext_list

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


if __name__ == '__main__':
    configure_logging()
    config = get_config()
    ext_config = get_ext_config()
    start_bot(config, ext_config)
