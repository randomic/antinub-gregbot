import logging

from discord.ext import commands


def setup(bot: commands.Bot):
    bot.add_cog(KillmailPoster(bot))


class KillmailPoster:
    def __init__(self, bot):
        self.logger = logging.getLogger(__name__)
        self.logger.info("%s %s", type(self).__name__, 2)
