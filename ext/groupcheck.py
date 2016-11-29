'''
Admin cog made by Steveizi for antinub-gregbot project.

Contains several commands regarding admin management
'''
import logging
import config

import discord.ext.commands as commands


def setup(bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(Admin(bot))


def is_owner(context):
    'Check whether or not the user is the owner of the bot'
    return calculate(context, 5)


def is_admin(context):
    'Check whether or not the user is an admin of the server'
    return calculate(context, 4)


def is_director(context):
    'Check whether or not the user is a director of the server'
    return calculate(context, 3)


def is_respected(context):
    'Check whether or not the user is a respected user of the server'
    return calculate(context, 2)


def is_member(context):
    'Check whether or not the user is a member of the server'
    return calculate(context, 1)


def calculate(context, level: int):
    '''Checks whether the user has a high enough "level" of permissions by
    comparing a pre-defined list of group permissions with the level of
    permission given as an argument'''
    role_list = context.message.author.roles
    server_id = context.message.server.id
    if context.message.author.id == config.OWNER_ID:
        return True
    else:
        for role in role_list:
            if role.name in config.UTIL['groups']:
                if config.UTIL['groups'][server_id][role.name] > level:
                    return True


class GroupManagement:
    '''A cog defining commands regarding group management
    and group checks'''
    def __init__(self, bot):
        self.logger = logging.getLogger(__name__)
        self.bot = bot

    get_status = '\n  \u2714 Cog loaded, ready to use'

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
    async def promote(self, ctx, promotee: str, role: str):
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
            for serverrole in server.roles:
                if role.name == role:
                    roleobj = serverrole
            if roleobj is None:
                await self.bot.say('Role not found on the server.')
                self.logger.warning('User entered an invalid role.')
            await self.bot.add_roles(member, roleobj)
            await self.bot.say('%s promoted to %s!' % promotee, role)

    @commands.command(pass_context=True)
    @commands.check(is_owner)
    async def demote(self, ctx, demotee: str, role: str):
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
            for serverrole in server.roles:
                if role.name == role:
                    roleobj = serverrole
            if roleobj is None:
                await self.bot.say('Role not found on the server.')
                self.logger.warning('User entered an invalid role.')
            await self.bot.remove_roles(member, roleobj)
            await self.bot.say('%s demoted from %s!' % demotee, role)

    @commands.command()
    @commands.check(is_admin)
    async def isadmin(self):
        '''Checks if the user is an admin'''
        await self.bot.say('Congrats, you\'re an admin. Fuck you')