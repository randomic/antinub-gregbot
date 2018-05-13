'''
Main helper cog made for antinub-gregbot project.

Contains several commands useful for controlling/debugging the bot
'''
import logging
import sys
from collections import deque
from traceback import _format_final_exc_line, format_exception

import discord.ext.commands as commands

import utils.checks as checks
from utils.messaging import Paginate, notify_owner


def setup(bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(Control(bot))


class Control:
    '''A cog defining commands for controlling the
    bot's operation such as stopping the bot'''

    def __init__(self, bot):
        self.logger = logging.getLogger(__name__)
        self.bot = bot

        # Override default event exception handling
        self.bot.on_error = self.on_error
        self.last_error = []

    async def error_notification(self, message, exc_info):
        'Send an error notification to the bot owner'
        paginate = Paginate(''.join(format_exception(*exc_info)),
                            ('```Python\n', '```'))
        notification = [paginate.prefix_next(message)] + list(paginate)

        if notification != self.last_error:
            await notify_owner(self.bot, notification)
            self.last_error = notification

    async def on_error(self, event, *dummy_args, **dummy_kwargs):
        'Assign a handler for errors raised by events'
        message = "Exception in `{}` event:".format(event)
        exc_info = sys.exc_info()
        self.logger.error(message, exc_info=exc_info)
        await self.error_notification(message, exc_info)

    async def on_command_error(self, exception, ctx):
        'Assign a handler for errors raised by commands'
        logger = self.logger if not ctx.cog else ctx.cog.logger

        if isinstance(exception, commands.CheckFailure):
            logger.warning('{} {} attempted to use `{}` command'.format(
                ctx.message.author.name, ctx.message.author.mention,
                ctx.command))
        elif isinstance(exception, commands.CommandNotFound):
            logger.info(exception)
        else:
            message = "Exception in `{}` command:".format(ctx.command)
            exc_info = (type(exception), exception, exception.__traceback__)
            logger.error(message, exc_info=exc_info)
            await self.error_notification(message, exc_info)

    @commands.command()
    @commands.check(checks.is_owner)
    async def stop(self):
        'Logs the bot out of discord and stops it'
        self.logger.info('Unloading extensions')
        extensions = self.bot.extensions.copy()
        for extension in extensions.keys():
            self.bot.unload_extension(extension)
        await self.bot.say('до свидания')
        self.logger.info('Logging out')
        await self.bot.logout()

    @commands.command()
    @commands.check(checks.is_owner)
    async def log(self, logname: str = 'error', n_lines: int = 10):
        'The bot posts the last n (default 10) lines of the specified logfile'
        try:
            n_lines = int(logname)
            logname = 'error'
        except ValueError:
            pass

        if n_lines <= 0:
            await self.bot.say('Invalid number of lines to display')
            return

        for handler in logging.getLogger().handlers:
            if isinstance(handler, logging.FileHandler):
                if handler.get_name() == logname:
                    path = handler.baseFilename
                    break
        else:
            await self.bot.say('No handler exists by that name.')
            return

        try:
            with open(path, 'rt') as log:
                lines = deque(log, n_lines)
            pref_str = 'Here are the last {} lines of the {} log:\n'
            pref = pref_str.format(n_lines, logname)
            body = ''.join(lines)

            if body:  # Only continue if there is something to show
                paginate = Paginate(body)

                await self.bot.say(paginate.prefix_next(pref))
                for page in paginate:
                    await self.bot.say(page)
            else:
                await self.bot.say('Log is empty')
        except FileNotFoundError:
            await self.bot.say('Specified log file does not exist')

    def get_health(self):
        'Returns a string describing the status of this cog'
        if self.bot.is_logged_in:
            return '\n  \u2714 Logged in as {}, id: {}'.format(
                self.bot.user.name, self.bot.user.id)

        return '\n  \u2716 Bot is not currently logged in'

    @commands.command()
    @commands.check(checks.is_owner)
    async def healthcheck(self, *args: str):
        'Returns the status of the named cog(s)'
        if not args:
            args = self.bot.cogs

        response = ''
        for name in args:
            if name in self.bot.cogs:
                cog = self.bot.cogs[name]
                try:
                    report = cog.get_health()
                    response += '{}: {}\n'.format(name, report)
                except AttributeError as exc:
                    self.logger.warning(exc)
            else:
                response += '{}:\n  \u2716 No such extension\n'.format(name)

        for page in Paginate(response):
            await self.bot.say(page)

    @commands.group(pass_context=True)
    @commands.check(checks.is_owner)
    async def ext(self, ctx):
        'Group of commands regarding loading and unloading of extensions'
        if not ctx.invoked_subcommand:
            resp = 'Usage: {}ext [list | load | unload | reload]'
            await self.bot.say(resp.format(ctx.prefix))

    @ext.command(name='list')
    async def ext_list(self):
        'List the currently loaded extensions'
        extensions = self.bot.config['loaded_extensions']

        if extensions:
            response = 'Currently loaded extensions:\n```\n'
            response += '\n'.join(sorted(extensions))
            response += '```'
        else:
            response = 'No extensions currently loaded'

        await self.bot.say(response)

    @ext.command()
    async def load(self, name: str = ''):
        'Attempt to load the specified extension'
        if not name:
            await self.bot.say('You must specify an extension to load')
            return

        plain_name = name.replace('.', '')
        if plain_name.startswith('ext'):
            plain_name = plain_name[3:]
        lib_name = 'ext.{}'.format(plain_name)

        if lib_name in self.bot.extensions:
            await self.bot.say('`{}` extension is already loaded'
                               .format(plain_name))
            return

        try:
            self.bot.load_extension(lib_name)
            self.logger.info('Successfully loaded extension: %s', plain_name)
            await self.bot.say('Successfully loaded extension: `{}`'
                               .format(plain_name))
            loaded_extensions = self.bot.config['loaded_extensions']
            loaded_extensions.append(plain_name)
            self.bot.config['loaded_extensions'] = loaded_extensions
        except Exception as exc:
            if isinstance(exc, ModuleNotFoundError) and getattr(
                    exc, "name") == lib_name:
                await self.bot.say('Extension not found: `{}`'
                                   .format(name))
                return

            error_str = _format_final_exc_line(type(exc).__qualname__,
                                               exc).strip()
            self.logger.warning('Failed to load extension: %s - %s',
                                plain_name, error_str)
            await self.bot.say('Failed to load extension: `{}` - `{}`'.format(
                plain_name, error_str))
            if lib_name in sys.modules:
                del sys.modules[lib_name]

    @ext.command()
    async def unload(self, name: str = ''):
        'Attempt to unload the specified extension'
        if name:
            plain_name = name.replace('.', '')
            if plain_name.startswith('ext'):
                plain_name = plain_name[3:]
            lib_name = 'ext.{}'.format(plain_name)

            if lib_name in self.bot.extensions:
                self.bot.unload_extension(lib_name)
                self.logger.info('Successfully unloaded extension: %s',
                                 plain_name)
                await self.bot.say('Successfully unloaded extension: `{}`'
                                   .format(plain_name))
                loaded_extensions = self.bot.config['loaded_extensions']
                loaded_extensions.remove(plain_name)
                self.bot.config['loaded_extensions'] = loaded_extensions
            else:
                await self.bot.say('`{}` extension is not loaded'
                                   .format(plain_name))
        else:
            await self.bot.say('You must specify an extension to unload')

    @ext.command(name='reload')
    async def ext_reload(self, name: str = ''):
        'Attempt to unload then load the specified extension'
        if name:
            plain_name = name.replace('.', '')
            if plain_name.startswith('ext'):
                plain_name = plain_name[3:]
            lib_name = 'ext.{}'.format(plain_name)

            if lib_name in self.bot.extensions:
                self.bot.unload_extension(lib_name)
                self.logger.info('Successfully unloaded extension: %s',
                                 plain_name)
                try:
                    self.bot.load_extension(lib_name)
                    self.logger.info('Successfully loaded extension: %s',
                                     plain_name)
                    await self.bot.say('Successfully reloaded extension: `{}`'
                                       .format(plain_name))
                except Exception as exc:
                    self.logger.warning('Failed to reload extension: %s - %s',
                                        plain_name, exc)
                    await self.bot.say('Failed to reload extension: `{}`'
                                       .format(plain_name))
            else:
                await self.bot.say('`{}` extension is not loaded'
                                   .format(plain_name))
        else:
            await self.bot.say('You must specify an extension to reload')
