import logging
from util import is_owner

import discord.ext.commands as commands


def setup(bot):
    bot.add_cog(Admin(bot))


def is_admin(context):
    'Check whether or not the user is an admin of the server'
    top_role = str(context.message.author.top_role)
    admin_role = "admin"
    if is_owner(context):
        return True
    else:
        return top_role == admin_role


class Admin:
    '''A cog defining commands for controlling the
    bot's operation such as stopping the bot'''
    def __init__(self, bot):
        self.logger = logging.getLogger(__name__)
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.check(is_owner)
    async def promote(self, ctx, promotee: str):
        '''Command that promotes a user via ID or name to a role called
        "admin", given that it has the permissions and the role exists.
        ID is most accurate, then Name#0000, then Name.'''
        if ctx.message.server is not None:
            server = ctx.message.server
            self.logger.info('Kappa1')
            if promotee.isdecimal():
                member = server.get_member(promotee)
                self.logger.info('User entered valid ID: %s', promotee)
            else:
                member = server.get_member_named(promotee)
                self.logger.info('User entered valid name: %s', promotee)
            if member is not None:
                await self.bot.say('Invalid member name/ID entered.')
                self.logger.warning('User entered invalid Name or ID')
            else:
                roles = ['admin']
                await server.add_roles(member, roles)
                await self.bot.say('%s promoted to admin!' % member.name)
        else:
            await self.bot.say('You can\'t promote someone in a private chat.')
            self.logger.warning('User tried to promote in PM')
