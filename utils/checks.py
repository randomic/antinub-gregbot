'''
Command checks cog made for antinub-gregbot project.
'''
from discord import PrivateChannel

import config


def is_owner(ctx):
    'Check whether or not the user is the owner of the bot'
    return ctx.message.author.id == config.OWNER_ID


def is_admin(ctx):
    'Check whether or not the user is an admin for the bot'
    if ctx.message.author.id == config.OWNER_ID:
        return True

    return ctx.message.author.id in config.ADMINS


def is_private_channel(ctx):
    'Check whether or not the context channel is a PrivateChannel'
    return isinstance(ctx.message.channel, PrivateChannel)
