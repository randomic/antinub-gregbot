import sys

from discord.ext import commands


def setup(bot: commands.Bot):
    'Adds the cog to the provided discord bot'
    sub_extensions = []

    try:
        name = '{}.listener'.format(__name__)
        bot.load_extension(name)
        sub_extensions.append(name)

        name = '{}.poster'.format(__name__)
        bot.load_extension(name)
        sub_extensions.append(name)
    except Exception as exception:
        message = "{} {}".format(name, str(exception))
        for extension in sub_extensions:
            bot.unload_extension(extension)
        del sys.modules[name]
        raise type(exception)(message) from exception


def teardown(bot: commands.Bot):
    bot.unload_extension('{}.poster'.format(__name__))
    bot.unload_extension('{}.listener'.format(__name__))
