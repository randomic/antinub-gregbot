from .aggregator import PingAggregator

from config import JABBER


def setup(bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(PingAggregator(bot, JABBER))
