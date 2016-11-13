'''
Main helper cog made for antinub-gregbot project.

Contains several commands useful for controlling/debugging the bot
'''
import logging
import os
from collections import deque

import discord.ext.commands as commands

import config


def setup(bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(Control(bot))


# Helper functions
def is_owner(context):
    'Check whether or not the user is the owner of the bot'
    return context.message.author.id == config.OWNER_ID


def paginate(string, pref='```', suff='```', max_length=2000, sep='\n'):
    'Chops a string into even chunks of max_length around the given separator'
    max_size = max_length - len(pref) - len(suff) + len(sep)
    str_length = len(string)
    if str_length <= max_size:
        return [pref + string + suff]
    else:
        split = string.rfind(sep, 0, max_size) + 1
        if split:
            return ([pref + string[:split-1] + suff]
                    + paginate(string[split:], pref, suff, max_length, sep))
        else:
            return ([pref + string[:max_size] + suff]
                    + paginate(string[max_size:], pref, suff, max_length, sep))


class Control:
    '''A cog defining commands for controlling the
    bot's operation such as stopping the bot'''
    def __init__(self, bot):
        self.logger = logging.getLogger(__name__)
        self.bot = bot

    async def on_command_error(self, exception, context):
        #TODO: Handle command errors better
        self.logger.debug(exception)

    @commands.command()
    @commands.check(is_owner)
    async def stop(self):
        'Logs the bot out of discord and stops it'
        await self.bot.say('до свидания')
        self.logger.info('Stopping bot on command')
        await self.bot.logout()

    @commands.command()
    @commands.check(is_owner)
    async def debug(self, n_lines: int=10):
        'The bot posts the last n (default 10) lines of its logfile'
        with open(os.path.join(config.LOG_PATH, 'info.log'), 'rt') as log:
            lines = deque(log, n_lines)
        pref = 'Here are the last %s lines of the log:\n' % n_lines
        body = ''.join(lines)

        # NOTE: Could be changed if discord increases the char limit
        responses = paginate(body)

        await self.bot.say(pref)
        for response in responses:
            await self.bot.say(response)

