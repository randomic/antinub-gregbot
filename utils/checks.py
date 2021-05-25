'''
Command checks cog made for antinub-gregbot project.
'''
from discord.abc import PrivateChannel


def is_owner(ctx):
    'Check whether or not the user is the owner of the bot'
    return str(ctx.message.author.id) == ctx.bot.owner_id


def is_private_channel(ctx):
    'Check whether or not the context channel is a PrivateChannel'
    return isinstance(ctx.message.channel, PrivateChannel)

def is_owner_private_channel(ctx):
    'Check whether or not the context is a PrivateChannel of the owner of the bot'
    return is_owner(ctx) and is_private_channel(ctx)
