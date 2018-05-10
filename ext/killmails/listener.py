'''
Killmail fetching cog for antinub-gregbot project.

Polls zKillboard's redisQ API and dispatches relevant killmails as an event.
'''
import logging
from asyncio import sleep

import discord.ext.commands as commands

from utils.messaging import notify_owner


class RedisQListener:
    '''Polls zKillboard's redisQ API and dispatches events containing killmails
    which pass the relevancy test'''
    redisq_polling_task = None

    def __init__(self, bot: commands.Bot):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.bot.loop.create_task(self.say_something())

    async def say_something(self):
        await sleep(10)
        await notify_owner(self.bot, ['bepis'])
