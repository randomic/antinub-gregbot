import logging
import config

import discord.ext.commands as commands

import os
from collections import deque


def setup(bot):
    bot.add_cog(Control(bot))


# Helper functions
def isOwner(context):
    'Check whether or not the user is the owner of the bot'
    return context.message.author.id == config.OWNER_ID

def segment(string, max_length, sep=''):
    '''Chops a string into even chunks of
    max_length around the given separator'''
    n = len(string)
    if n <= max_length:
        return [string]
    else:
        x = string.rfind(sep, 0, max_length) + 1
        if not x: x = max_length
        return [string[:x]] + segment(string[x:], max_length, sep)


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
    @commands.check(isOwner)
    async def stop(self):
        'Logs the bot out of discord and stops it'
        await self.bot.say('до свидания')
        await self.bot.logout()
    
    @commands.command()
    @commands.check(isOwner)
    async def debug(self, n : int = 10):
        'The bot posts the last n (default 10) lines of its logfile'
        with open(os.path.join(config.LOG_PATH, 'info.log'), 'rt') as f:
            lines = deque(f, n)
        pref = 'Here are the last %s lines of the log:\n' % n
        body = ''.join(lines)
        form = '```'

        responses = segment(body, 1800, '\n')

        await self.bot.say(pref)
        for response in responses:
            await self.bot.say(form + response + form)