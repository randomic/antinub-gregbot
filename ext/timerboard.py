import logging
import config
import datetime
import json

import discord.ext.commands as commands


def setup(bot):
    bot.add_cog(Timerboard(bot))


# Helper functions
def isOwner(context):
    'Check whether or not the user is the owner of the bot'
    return context.message.author.id == config.OWNER_ID


class Timerboard:
    '''A cog defining commands for controlling the
    bot's timerboard functions'''
    def __init__(self, bot):
        self.logger = logging.getLogger(__name__)

        self.bot = bot

    async def on_command_error(self, exception, context):
        self.logger.debug(type(exception))
    
    def loadjson(self, jsonname):
        try:
            with open(jsonname) as data_file:
                data = json.load(data_file)
            return data
            self.logger.info('Json successfully loaded.')
        except FileNotFoundError:
            return {
            'fleettime' : 0,
        }
        
    def savejson(self, data, jsonname):
        try:
            with open(jsonname, 'wt') as outfile:
                json.dump(data, outfile)
            self.logger.info('Json successfully saved.')
        except TypeError as e:
            self.logger.error(e)

    @commands.command()
    @commands.check(isOwner)
    async def addfleet(self, FDATE: str, FTIME: str, FC: str, FORMUP: str, DOCT: str, FTYPE: str):
        '''Adds a fleet to the list of fleets in the json.
        Input fleets in the format "DD/MM/YYYY MM/HH FC FORMUP DOCTRINE FLEETTYPE'''
        FINFO = str(FDATE + FTIME)
        self.logger.info(FINFO)
        try:
            fleetdtime = datetime.strptime(FINFO, '%d/%m/%Y%H:%M')
            self.logger.info('Converted to datetime')
        except:
            self.logger.info('Failed to convert to datetime')
        
        self.fleetjson = loadjson("fleetlist.json")
        self.fleetjson["fleets"].append({
            'fleettime' : fleetdtime,
            'fc' : FC,
            'formup' : FORMUP,
            'doctrine' : DOCT,
            'fleettype' : FTYPE
        })
        self.savejson(self.fleetjson, 'fleetlist.json')
        await self.bot.say(self.fleetjson["fleets"])
        
    @commands.command()
    async def datetime(self):
        currentdate = datetime.datetime.now()
        self.logger.info(currentdate)
        await self.bot.say(currentdate)
    
    @commands.command()
    async def customdatetime(self, date : datetime):
        await self.bot.say(date)
        self.logger.info(date)
        