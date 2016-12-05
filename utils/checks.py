'''
Command checks cog made for antinub-gregbot project.
'''
import config


def is_owner(ctx):
    'Check whether or not the user is the owner of the bot'
    return ctx.message.author.id == config.OWNER_ID
