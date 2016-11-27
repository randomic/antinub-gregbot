'''
Admin cog made by Steveizi for antinub-gregbot project.

Contains several commands regarding admin management
'''
import logging
from util import is_owner

import discord.ext.commands as commands


def setup(bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(Admin(bot))


def is_admin(context):
    'Check whether or not the user is an admin of the server'
    role_list = context.message.author.roles
    admin_role = "admin"
    if is_owner(context):
        return True
    else:
        for role in role_list:
            if role.name == admin_role:
                return True


class Admin:
    '''A cog defining commands for controlling the
    bot's operation such as stopping the bot'''
    def __init__(self, bot):
        self.logger = logging.getLogger(__name__)
        self.bot = bot

    def get_status(self):
        'Returns a string describing the status of this cog'
        return '\n  \u2714 Cog loaded, ready to use'

    def get_memberobj(self, context, user):
        '''A function which returns either a member object of the given
        ID/User or None if it cannot get it'''
        if context.message.server is not None:
            server = context.message.server
            if user.isdecimal():
                self.logger.info('User entered valid ID: %s', user)
                return server.get_member(user)
            else:
                self.logger.info('User entered valid name: %s', user)
                return server.get_member_named(user)
        else:
            return "PM"

    @commands.command(pass_context=True)
    @commands.check(is_owner)
    async def promote(self, ctx, promotee: str):
        '''Command that promotes a user via ID or name to a role called
        "admin", given that it has the permissions and the role exists.
        ID is most accurate, then Name#0000, then Name.'''
        member = self.get_memberobj(ctx, promotee)
        if member is None:
            await self.bot.say('Invalid member name/ID entered.')
            self.logger.warning('User entered invalid Name or ID')
        elif member == "PM":
            await self.bot.say('You can\'t promote someone in a private chat.')
            self.logger.warning('User tried to promote in PM')
        else:
            roleobj = None
            server = ctx.message.server
            for role in server.roles:
                if role.name == 'admin':
                    roleobj = role
            await self.bot.add_roles(member, roleobj)
            await self.bot.say('%s promoted to admin!' % promotee)

    @commands.command(pass_context=True)
    @commands.check(is_owner)
    async def demote(self, ctx, demotee: str):
        '''Command that demotes a user via ID or name from a role called
        "admin", given that it has the permissions and the role exists.
        ID is most accurate, then Name#0000, then Name.'''
        member = self.get_memberobj(ctx, demotee)
        if member is None:
            await self.bot.say('Invalid member name/ID entered.')
            self.logger.warning('User entered invalid Name or ID')
        elif member == "PM":
            await self.bot.say('You can\'t demote someone in a private chat.')
            self.logger.warning('User tried to demote in PM')
        else:
            roleobj = None
            server = ctx.message.server
            for role in server.roles:
                if role.name == 'admin':
                    roleobj = role
            await self.bot.remove_roles(member, roleobj)
            await self.bot.say('%s demoted from admin!' % demotee)

    @commands.command()
    @commands.check(is_admin)
    async def isadmin(self):
        '''Checks if the user is an admin'''
        await self.bot.say('Congrats, you\'re an admin.')
