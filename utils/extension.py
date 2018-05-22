import inspect
import sys
import typing

from discord.ext import commands


def configure(sub_extensions: typing.List[str]) -> None:
    caller = inspect.stack()[1]
    module = inspect.getmodule(caller[0])
    module.setup = setup(module, sub_extensions)
    module.teardown = teardown(module, sub_extensions)


def setup(module: typing.types.ModuleType,
          sub_extensions: typing.List[str]) -> typing.Callable:
    'Adds the cog to the provided discord bot'

    def inner(bot: commands.Bot):
        try:
            for extension in sub_extensions:
                name = '{}.{}'.format(module.__name__, extension)
                bot.load_extension(name)
        except Exception as exception:
            message = "{} ({})".format(str(exception), name)
            for extension in sub_extensions:
                name = '{}.{}'.format(module.__name__, extension)
                bot.unload_extension(name)
                if name in sys.modules:
                    del sys.modules[name]
            raise type(exception)(message).with_traceback(
                exception.__traceback__) from None

    return inner


def teardown(module: typing.types.ModuleType,
             sub_extensions: typing.List[str]) -> typing.Callable:
    def inner(bot: commands.Bot):
        for extension in sub_extensions:
            name = '{}.{}'.format(module.__name__, extension)
            bot.unload_extension(name)

    return inner
