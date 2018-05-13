'''
Killmail fetching cog for antinub-gregbot project.

Polls zKillboard's redisQ API and dispatches relevant killmails as an event.
'''
import asyncio
import logging

import aiohttp
import discord.ext.commands as commands

REDISQ_URL = 'https://redisq.zkillboard.com/listen.php'
INITIAL_BACKOFF = 0.1
MAXIMUM_BACKOFF = 3600
EXPONENTIAL_BACKOFF_FACTOR = 2


def setup(bot: commands.Bot):
    bot.add_cog(RedisQListener(bot))


class RedisQListener:
    '''Polls zKillboard's redisQ API and dispatches events containing killmails
    which pass the relevancy test'''
    backoff_wait = INITIAL_BACKOFF

    def __init__(self, bot: commands.Bot):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.redisq_polling_task = self.listen_task_start()

    def __unload(self):
        self.redisq_polling_task.cancel()

    def listen_task_start(self) -> asyncio.Task:
        task = self.bot.loop.create_task(self.wait_for_package())
        task.add_done_callback(self.listen_task_done)
        return task

    def listen_task_done(self, task: asyncio.Task):
        try:
            package = task.result()
            self.bot.dispatch('killmail', package)
        except asyncio.CancelledError:
            return
        except FetchError as exception:
            self.logger.warning(exception)
        except Exception:
            message = 'Unexpected error in RedisQ polling'
            self.logger.exception(message)

        self.redisq_polling_task = self.listen_task_start()

    async def wait_for_package(self):
        delay = min(self.backoff_wait, MAXIMUM_BACKOFF)
        await asyncio.sleep(delay)
        try:
            async with self.bot.http.session.get(REDISQ_URL) as resp:
                resp.raise_for_status()
                self.backoff_wait = INITIAL_BACKOFF
                package = await resp.json()
                if package['package']:
                    return package
                self.logger.debug('RedisQ returned null package')

        except (aiohttp.errors.HttpProcessingError,
                aiohttp.errors.ClientResponseError,
                aiohttp.errors.ClientRequestError,
                aiohttp.errors.ClientOSError,
                aiohttp.errors.ClientDisconnectedError,
                aiohttp.errors.ClientTimeoutError,
                asyncio.TimeoutError) as exception:
            self.backoff_wait *= EXPONENTIAL_BACKOFF_FACTOR

            if hasattr(exception, 'code'):
                message = 'Response from RedisQ: {} {}'.format(
                    exception.code, exception.message)
            else:
                message = 'Error reaching RedisQ: {}'.format(exception)
            raise FetchError(message)

    def process_result(self, package: dict):
        raise NotImplementedError


class FetchError(Exception):
    pass
