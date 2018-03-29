from .aggregator import Aggregator

from config import JABBER


def setup(bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(Aggregator(bot, JABBER))
