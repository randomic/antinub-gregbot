'KappaPride (NinjaCode2k16[tm])'
import logging
import datetime
import json

import discord.ext.commands as commands

from ext.util import isOwner


def setup(bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(Timerboard(bot))


class Timerboard:
    '''A cog defining commands for controlling the
    bot's timerboard functions'''
    def __init__(self, bot):
        self.logger = logging.getLogger(__name__)
        self.fleetjson = None
        self.bot = bot

    def loadjson(self, jsonname):
        'A function which loads a json, given the filename'
        try:
            with open(jsonname) as data_file:
                data = json.load(data_file)
            self.logger.info('Json successfully loaded.')
            return data
        except FileNotFoundError:
            return {
                "fleets": []
            }

    def savejson(self, data, jsonname):
        'A function which saves a json, given the filename'
        try:
            with open(jsonname, 'wt') as outfile:
                json.dump(data, outfile)
            self.logger.info('Json successfully saved.')
        except TypeError as error:
            self.logger.error(error)

    @commands.command()
    @commands.check(isOwner)
    async def addfleet(self, fdate: str, ftime: str, flco: str, formup: str, doct: str, ftype: str):
        '''Adds a fleet to the list of fleets in the json.
        Input fleets in the format
        "DD/MM/YYYY HH/MM FC FORMUP DOCTRINE FLEETTYPE'''
        fleetdtime = datetime.datetime.strptime((fdate + ftime), '%d/%m/%Y%H:%M')
        self.logger.info('Converted to datetime')

        self.fleetjson = self.loadjson("fleetlist.json")
        self.logger.info(self.fleetjson)
        self.fleetjson["fleets"].append({
            'fleettime': fleetdtime.isoformat(),
            'fc': flco,
            'formup': formup,
            'doctrine': doct,
            'fleettype': ftype
        })
        self.savejson(self.fleetjson, 'fleetlist.json')
        await self.bot.say(self.fleetjson["fleets"])

    @commands.command()
    @commands.check(isOwner)
    async def removefleet(self, number: str):
        'Removes a fleet from the json via number on the list of fleets'
        self.fleetjson = self.loadjson("fleetlist.json")
        try:
            number = int(number)
            if number >= 1:
                self.fleetjson['fleets'].pop(number-1)
                self.savejson(self.fleetjson, 'fleetlist.json')
                await self.bot.say(self.fleetjson["fleets"])
            else:
                await self.bot.say("You didn't enter a valid number.")
                self.logger.warning("User didn't enter a valid number.")
        except ValueError:
            self.logger.warning("User didn't enter an integer")
            await self.bot.say("Please enter an integer.")

    @commands.command()
    async def listfleets(self):
        'Lists all fleets to the chat in discord'
        self.fleetjson = self.loadjson("fleetlist.json")
        for fleet in self.fleetjson['fleets']:
            for info in self.fleetjson[fleet]:
                await self.bot.say(info, ':', self.fleetjson[info][fleet])

    @commands.command()
    async def datetime(self):
        'Prints the current datetime to the chat and logger'
        currentdate = datetime.datetime.now()
        self.logger.info(currentdate)
        await self.bot.say(currentdate)
