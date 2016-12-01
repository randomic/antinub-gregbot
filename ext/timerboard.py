'KappaPride (NinjaCode2k16[tm])'
import logging
import datetime
import json
from operator import itemgetter
from os.path import isfile
import ext.permcheck as permcheck
import discord.ext.commands as commands


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
            data['fleets'].sort(key=itemgetter('fleettime'))
            with open(jsonname, 'wt') as outfile:
                json.dump(data, outfile)
            self.logger.info('Json successfully saved.')
        except TypeError as error:
            self.logger.error(error)

    def listfleet(self, index, announce=False):
        'Returns a string containing the fleet details given an index'
        fleets = self.loadjson("fleetlist.json")['fleets']
        response = ""
        if announce:
            response += "@everyone\n"
        fleet = fleets[index]
        response += "**Fleet {}:**\n".format(index+1)
        ftime = datetime.datetime.strptime(fleet["fleettime"],
                                           '%Y-%m-%dT%H:%M:%S')
        response += "```When: {}\n".format(ftime)
        response += "FC: {}\n".format(fleet["fc"])
        response += "Type: {}\n".format(fleet['fleettype'])
        response += "Doctrine: {}\n".format(fleet['doctrine'])
        response += "Formup: {}```\n".format(fleet['formup'])
        self.logger.info(response)
        return response

    def get_health(self):
        '''Returns a string describing the status of this cog'''
        if isfile('fleetlist.json'):
            return '\n  \u2714 fleetlist.json exists'
        else:
            return '\n  \u2716 No fleetlist file found'

    @commands.command()
    @permcheck.three()
    async def addfleet(self, fdate: str, ftime: str, flco: str,
                       formup: str, doct: str, ftype: str):
        '''Adds a fleet to the list of fleets in the json.
        Input fleets in the format
        "DD/MM/YYYY HH/MM FC FORMUP DOCTRINE FLEETTYPE'''
        fleetdtime = datetime.datetime.strptime((fdate + ftime), '%d/%m/%Y%H:%M')
        self.logger.info('Converted to datetime')
        if fleetdtime <= datetime.datetime.now():
            await self.bot.say("Date entered is before the current date.")
            self.logger.warning("User entered an invalid date")
        else:
            self.fleetjson = self.loadjson("fleetlist.json")
            self.fleetjson["fleets"].append({
                'fleettime': fleetdtime.isoformat(),
                'fc': flco,
                'formup': formup,
                'doctrine': doct,
                'fleettype': ftype,
                'announced': False
            })
            self.savejson(self.fleetjson, 'fleetlist.json')
            await self.bot.say("Fleet successfully added!")

    @commands.command()
    @permcheck.three()
    async def removefleet(self, number: str):
        'Removes a fleet from the json via number on the list of fleets'
        self.fleetjson = self.loadjson("fleetlist.json")
        try:
            number = int(number)
            if number >= 1:
                self.fleetjson['fleets'].pop(number-1)
                self.savejson(self.fleetjson, 'fleetlist.json')
                await self.bot.say("Fleet %d successfully removed." % number)
            else:
                await self.bot.say("You didn't enter a valid number.")
                self.logger.warning("User didn't enter a valid number.")
        except ValueError:
            self.logger.warning("User didn't enter an integer")
            await self.bot.say("Please enter an integer.")

    @commands.command()
    @permcheck.two()
    async def listfleets(self):
        'Lists all fleets to the chat in discord'
        fleets = self.loadjson("fleetlist.json")['fleets']
        n_fleets = len(fleets)
        self.logger.info(fleets)
        listedfleets = 0
        for idx in range(n_fleets):
            if self.listfleet(idx) != []:
                await self.bot.say(self.listfleet(idx))
                listedfleets += 1
        if listedfleets == 0:
            await self.bot.say('No fleets to list.')

    @commands.command()
    @permcheck.three()
    async def announcefleets(self):
        'Announces all un-announced fleets'
        self.fleetjson = self.loadjson("fleetlist.json")
        n_fleets = len(self.fleetjson['fleets'])
        announced = False
        for idx in range(n_fleets):
            if not self.fleetjson['fleets'][idx]["announced"]:
                await self.bot.say(self.listfleet(idx, True))
                self.fleetjson['fleets'][idx]["announced"] = True
                self.savejson(self.fleetjson, 'fleetlist.json')
                announced = True
        if not announced:
            await self.bot.say("All Fleets Announced!")

    @commands.command()
    @permcheck.four()
    async def resetannouncefleets(self, number: str):
        '''Resets the boolean specifying whether a fleet has been announced.
        Enter a fleet number to reset a specific fleet or "all" to reset all'''
        self.fleetjson = self.loadjson("fleetlist.json")
        n_fleets = len(self.fleetjson['fleets'])
        if number.isdecimal():
            self.fleetjson['fleets'][int(number)-1]["announced"] = False
            self.savejson(self.fleetjson, 'fleetlist.json')
            await self.bot.say("Fleet %s's announcement status reset." % number)
            self.logger.info('User reset fleet %s\'s announcement status', number)
        elif number == "all":
            for idx in range(n_fleets):
                self.fleetjson['fleets'][idx]["announced"] = False
            self.savejson(self.fleetjson, 'fleetlist.json')
            await self.bot.say("All anouncement statuses reset.")
            self.logger.info('User reset all announcement statuses')
        else:
            error = "Enter a valid number to reset or 'all' to reset all"
            await self.bot.say(error)
            self.logger.warning('User entered an invalid number to reset.')
