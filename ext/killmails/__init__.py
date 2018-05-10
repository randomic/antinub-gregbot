from discord.ext.commands import Bot

from .listener import RedisQListener
from .poster import KillmailPoster


def setup(bot: Bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(RedisQListener(bot))
    bot.add_cog(KillmailPoster(bot))
