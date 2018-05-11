'''
Killmail fetching cog for antinub-gregbot project.

Polls zKillboard's redisQ API and dispatches relevant killmails as an event.
'''
import asyncio
import logging
from asyncio import sleep

import discord.ext.commands as commands

from utils.messaging import notify_owner


def setup(bot: commands.Bot):
    bot.add_cog(RedisQListener(bot))


class RedisQListener:
    '''Polls zKillboard's redisQ API and dispatches events containing killmails
    which pass the relevancy test'''
    redisq_polling_task = None

    def __init__(self, bot: commands.Bot):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.task = self.bot.loop.create_task(self.say_something())

    async def say_something(self):
        while True:
            await sleep(5)
            await notify_owner(self.bot, ['bepis'])

    def __unload(self):
        self.task.cancel()
        print("unloaded")
