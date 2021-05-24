"""
Cog containing EVE Online commands which can be used by anyone
"""
from datetime import datetime

import discord.ext.commands as commands

from utils.log import get_logger


def setup(bot):
    "Adds the cog to the provided discord bot"
    bot.add_cog(Eve(bot))


class Eve(commands.Cog, name="Eve"):
    def __init__(self, bot):
        self.logger = get_logger(__name__, bot)
        self.bot = bot
        self.fmt = "%H:%M:%S"

    @commands.command()
    async def evetime(self, ctx):
        return await ctx.send(
            "Current EVE time: " + datetime.utcnow().strftime(self.fmt))
