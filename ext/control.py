import logging
import config

import discord.ext.commands as commands


def setup(bot):
    bot.add_cog(Control(bot))


# Helper functions
def isOwner(context):
    'Check whether or not the user is the owner of the bot'
    return context.message.author.id == config.OWNER_ID


class Control:
    '''A cog defining commands for controlling the
    bot's operation such as stopping the bot'''
    def __init__(self, bot):
        self.logger = logging.getLogger(__name__)

        self.bot = bot

    async def on_command_error(self, exception, context):
        self.logger.debug(type(exception))

    @commands.command()
    @commands.check(isOwner)
    async def stop(self):
        '''Logs the bot out of discord and stops it'''
        await self.bot.say('до свидания')
        await self.bot.logout()
    
    @commands.command()
    async def wopolusa(self):
        '''Sends a picture of wopolusa to the chat'''
        await self.bot.say('http://i.imgur.com/wnwTGnf.png')