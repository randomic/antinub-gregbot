'''Fuck that default checker, we need our own! - Ninja for no reason'''
import logging
import config
from discord import Forbidden
import discord.ext.commands as commands


def setup(bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(Permcheck(bot))


def five():
    'My re-write of the shitty check command'
    def predicate(ctx):
        'By god, I think I did it'
        role_list = ctx.message.author.roles
        server_id = ctx.message.server.id
        groups = config.PERMCHECK['servers'][server_id]['groups']
        if ctx.message.author.id == config.OWNER_ID:
            return True
        else:
            for role in role_list:
                if role.name in groups:
                    if groups[role.name] >= 5:
                        return True
            return False

    return commands.check(predicate)


def four():
    'My re-write of the shitty check command'
    def predicate(ctx):
        'By god, I think I did it'
        role_list = ctx.message.author.roles
        server_id = ctx.message.server.id
        groups = config.PERMCHECK['servers'][server_id]['groups']
        if ctx.message.author.id == config.OWNER_ID:
            return True
        else:
            for role in role_list:
                if role.name in groups:
                    if groups[role.name] >= 4:
                        return True
            return False

    return commands.check(predicate)


def three():
    'My re-write of the shitty check command'
    def predicate(ctx):
        'By god, I think I did it'
        role_list = ctx.message.author.roles
        server_id = ctx.message.server.id
        groups = config.PERMCHECK['servers'][server_id]['groups']
        if ctx.message.author.id == config.OWNER_ID:
            return True
        else:
            for role in role_list:
                if role.name in groups:
                    if groups[role.name] >= 3:
                        return True
            return False

    return commands.check(predicate)


def two():
    'My re-write of the shitty check command'
    def predicate(ctx):
        'By god, I think I did it'
        role_list = ctx.message.author.roles
        server_id = ctx.message.server.id
        groups = config.PERMCHECK['servers'][server_id]['groups']
        if ctx.message.author.id == config.OWNER_ID:
            return True
        else:
            for role in role_list:
                if role.name in groups:
                    if groups[role.name] >= 2:
                        return True
            return False

    return commands.check(predicate)


def one():
    'My re-write of the shitty check command'
    def predicate(ctx):
        'By god, I think I did it'
        role_list = ctx.message.author.roles
        server_id = ctx.message.server.id
        groups = config.PERMCHECK['servers'][server_id]['groups']
        if ctx.message.author.id == config.OWNER_ID:
            return True
        else:
            for role in role_list:
                if role.name in groups:
                    if groups[role.name] >= 1:
                        return True
            return False

    return commands.check(predicate)


class Permcheck:
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
    @five()
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
                if serverrole.name == role:
                    roleobj = serverrole
                    self.logger.info('Role located')
            if roleobj is None:
                await self.bot.say('Role not found on the server.')
                self.logger.warning('User entered an invalid role.')
            try:
                await self.bot.add_roles(member, roleobj)
                await self.bot.say('{} promoted to {}'.format(promotee, role))
            except Forbidden:
                self.logger.warning('User tried to promote but the bot has '
                                    + 'insufficent roles on the server.')
                await self.bot.say('I have insufficent roles to promote on '
                                   + 'this server.')

    @commands.command(pass_context=True)
    @five()
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
                if serverrole.name == role:
                    roleobj = serverrole
                    self.logger.info('Role located')
            if roleobj is None:
                await self.bot.say('Role not found on the server.')
                self.logger.warning('User entered an invalid role.')
            try:
                await self.bot.add_roles(member, roleobj)
                await self.bot.say('{} demoted from {}'.format(demotee, role))
            except Forbidden:
                self.logger.warning('User tried to demote but the bot has '
                                    + 'insufficent roles on the server.')
                await self.bot.say('I have insufficent roles to demote on '
                                   + 'this server.')

    @commands.command()
    @four()
    async def isadmin(self):
        '''Checks if the user is an admin'''
        await self.bot.say('Congrats, you\'re an admin. Fuck you')
