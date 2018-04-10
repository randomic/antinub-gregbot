"""
Cog containing EVE Online commands which can be used by anyone
"""
import logging
from datetime import datetime

import discord.ext.commands as commands


def setup(bot):
    "Adds the cog to the provided discord bot"
    bot.add_cog(Eve(bot))


class Eve:
    def __init__(self, bot):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.fmt = "%H:%M:%S"

    @commands.command()
    async def evetime(self):
        return await self.bot.say(
            "Current EVE time: " + datetime.utcnow().strftime(self.fmt)
        )
