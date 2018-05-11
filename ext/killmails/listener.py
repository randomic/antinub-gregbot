'''
Killmail fetching cog for antinub-gregbot project.

Polls zKillboard's redisQ API and dispatches relevant killmails as an event.
'''
import logging

import discord.ext.commands as commands


def setup(bot: commands.Bot):
    bot.add_cog(RedisQListener(bot))


class RedisQListener:
    '''Polls zKillboard's redisQ API and dispatches events containing killmails
    which pass the relevancy test'''
    redisq_polling_task = None

    def __init__(self, bot: commands.Bot):
        self.logger = logging.getLogger(__name__)
        self.logger.info("%s %s", type(self).__name__, 3)
