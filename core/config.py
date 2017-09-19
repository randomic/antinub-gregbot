'''
Cog providing commands used for general configuration fo the bot.

'''
import logging

import discord.ext.commands as commands

import utils.checks as checks


def setup(bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(Config(bot))


class Config:
    '''A cog defining commands for configuring the bot

    '''
    def __init__(self, bot):
        self.logger = logging.getLogger(__name__)
        self.bot = bot

