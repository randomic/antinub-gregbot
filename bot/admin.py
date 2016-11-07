import logging
import config
import json
import discord

import discord.ext.commands as commands


def setup(client):
    client.add_cog(Admin(client))


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
    def __init__(self, client):
        self.logger = logging.getLogger(__name__)
        self.client = client
    
    def loadjson(self, jsonname):
        try:
            with open(jsonname) as data_file:
                data = json.load(data_file)
            return data
            self.logger.info('Json successfully loaded.')
        except FileNotFoundError:
            return {}
    
    def savejson(self, data, jsonname):
        try:
            with open(jsonname, 'wt') as outfile:
                json.dump(data, outfile)
            self.logger.info('Json successfully saved.')
        except TypeError as e:
            self.logger.error(e)
    

    
    async def on_command_error(self, exception, context):
            self.logger.debug(type(exception))
    
    @commands.command()
    @commands.check(isOwner)
    async def addadmin(self, ID : str):
        '''Makes a user admin via ID'''
        self.data = self.loadjson('adminlist.json')
        if ID.isdecimal() and not ID in self.data['admins'] and ID != config.OWNER_ID:
            self.data['admins'].append(ID)
            self.savejson(self.data, 'adminlist.json')
            self.logger.info('%s added as an admin' % ID)
            await self.client.say('%s added as an admin.' % ID)
        else:
            self.logger.warning('User entered invalid ID.')
            await self.client.say('You entered an invalid ID.')
    
    @commands.command()
    @commands.check(isOwner)
    async def removeadmin(self, ID : str):
        '''Removes a user from the admin list via ID'''
        self.data = self.loadjson('adminlist.json')
        if ID in self.data['admins']:
            self.data['admins'].remove(ID)
            self.savejson(self.data, 'adminlist.json')
            self.logger.info('%s removed from the admin list.' % ID)
            await self.client.say('%s has been removed from the admin list.' % ID)
        else:
            self.logger.warning('User entered invalid ID: %s', ID)
            await self.client.say('You entered an invalid ID.')
    
    @commands.command()
    @commands.check(isAdmin)
    async def listadmins(self):
        '''Prints a list of the admin ID's to the chat.'''
        self.data = self.loadjson('adminlist.json')
        self.logger.info('User listed admin ID\'s')
        await self.client.say('**-------- ADMINS --------**')
        for admin in self.data['admins']:
            try: 
                user = await self.client.get_user_info(admin)
                self.logger.info("%s - %s", user.name, user.id)
                await self.client.say('**User:** %s, **ID:** %s' % (user.name, user.id))
            except discord.errors.NotFound as e:
                self.logger.info('NotFound - %s', admin)
                await self.client.say('**User:** NotFound (Is this a valid ID?), **ID:** %s' % admin)
                
    @commands.command()
    @commands.check(isAdmin)
    async def isadmin(self):
        '''Checks if the user is an admin'''
        self.logger.info('User checked if they were an admin')
        await self.client.say('You are an admin! Congratulations but you still suck.')