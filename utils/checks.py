'''
Command checks cog made for antinub-gregbot project.
'''
from discord import PrivateChannel


def is_owner(ctx):
    'Check whether or not the user is the owner of the bot'
    return ctx.message.author.id == ctx.bot.config.get('owner_id')


def is_private_channel(ctx):
    'Check whether or not the context channel is a PrivateChannel'
    return isinstance(ctx.message.channel, PrivateChannel)
