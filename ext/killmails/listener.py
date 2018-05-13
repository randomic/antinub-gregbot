'''
Killmail fetching cog for antinub-gregbot project.

Polls zKillboard's redisQ API and dispatches relevant killmails as an event.
'''
import asyncio
import logging
from http.client import responses

import aiohttp
import discord.ext.commands as commands

REDISQ_URL = 'https://redisq.zkillboard.com/listen.php'


def setup(bot: commands.Bot):
    bot.add_cog(RedisQListener(bot))


class RedisQListener:
    '''Polls zKillboard's redisQ API and dispatches events containing killmails
    which pass the relevancy test'''

    def __init__(self, bot: commands.Bot):
        self.logger = logging.getLogger(__name__)
        self.logger.info('%s %s', type(self).__name__, 3)
        self.bot = bot
        self.redisq_polling_task = self.listen_task_start()

    def __unload(self):
        self.redisq_polling_task.cancel()

    def listen_task_start(self, delay: int = 0) -> asyncio.Task:
        task = self.bot.loop.create_task(self.wait_for_package(delay))
        task.add_done_callback(self.listen_task_done)
        return task

    def listen_task_done(self, task: asyncio.Task):
        delay = 0
        try:
            package = task.result()
            self.process_result(package)
        except asyncio.CancelledError:
            return
        except Exception:
            message = 'Unexpected error in killmail retrieval'
            self.logger.exception(message)
            delay = 10

        self.listen_task_start(delay)

    async def wait_for_package(self, delay: int):
        await asyncio.sleep(delay)
        async with self.bot.http.session.get(REDISQ_URL) as resp:
            self.logger.info('Response from RedisQ: %s %s', resp.status,
                             responses[resp.status])

    def process_result(self, package: dict):
        raise NotImplementedError
