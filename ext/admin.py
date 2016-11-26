import logging
import config
import json
import discord

import discord.ext.commands as commands


def setup(bot):
    bot.add_cog(Admin(bot))


# Helper functions
def isOwner(context):
    'Check whether or not the user is the owner of the bot'
    return context.message.author.id == config.OWNER_ID

def isAdmin(context):
    '''Check whether or not the user is an admin of the bot'''
    if isOwner(context):
        return True
    else:
        with open('adminlist.json') as data_file:
            adminList = json.load(data_file)
        return context.message.author.id in adminList['admins']

class Admin:
    '''A cog defining commands for controlling the
    bot's operation such as stopping the bot'''
    def __init__(self, bot):
        self.logger = logging.getLogger(__name__)
        self.bot = bot

    def loadjson(self, jsonname):
        try:
            with open(jsonname) as data_file:
                data = json.load(data_file)
                self.logger.info('Json successfully loaded.')
            return data
        except FileNotFoundError:
            return {'admins' : []}

    def savejson(self, data, jsonname):
        try:
            with open(jsonname, 'wt') as outfile:
                json.dump(data, outfile)
            self.logger.info('Json successfully saved.')
        except TypeError as e:
            self.logger.error(e)

    @commands.command()
    @commands.check(isOwner)
    async def addadmin(self, ID : str):
        '''Makes a user admin via ID'''
        self.data = self.loadjson('adminlist.json')
        if ID.isdecimal() and not ID in self.data['admins'] and ID != config.OWNER_ID:
            self.data['admins'].append(ID)
            self.savejson(self.data, 'adminlist.json')
            self.logger.info('%s added as an admin' % ID)
            await self.bot.say('%s added as an admin.' % ID)
        else:
            self.logger.warning('User entered invalid ID.')
            await self.bot.say('You entered an invalid ID.')

    @commands.command()
    @commands.check(isOwner)
    async def removeadmin(self, ID : str):
        '''Removes a user from the admin list via ID'''
        self.data = self.loadjson('adminlist.json')
        if ID in self.data['admins']:
            self.data['admins'].remove(ID)
            self.savejson(self.data, 'adminlist.json')
            self.logger.info('%s removed from the admin list.' % ID)
            await self.bot.say('%s has been removed from the admin list.' % ID)
        else:
            self.logger.warning('User entered invalid ID: %s', ID)
            await self.bot.say('You entered an invalid ID.')

    @commands.command()
    @commands.check(isAdmin)
    async def listadmins(self):
        '''Prints a list of the admin ID's to the chat.'''
        self.data = self.loadjson('adminlist.json')
        self.logger.info('User listed admin ID\'s')
        await self.bot.say('**-------- ADMINS --------**')
        for admin in self.data['admins']:
            try:
                user = await self.bot.get_user_info(admin)
                self.logger.info("%s - %s", user.name, user.id)
                await self.bot.say('**User:** %s, **ID:** %s' % (user.name, user.id))
            except discord.errors.NotFound as e:
                self.logger.info('NotFound - %s', admin)
                await self.bot.say('**User:** NotFound (Is this a valid ID?), **ID:** %s' % admin)

    @commands.command()
    @commands.check(isAdmin)
    async def isadmin(self):
        '''Checks if the user is an admin'''
        self.logger.info('User checked if they were an admin')
        await self.bot.say('You are an admin! Congratulations but you still suck.')