'KappaPride (NinjaCode2k16[tm])'
import datetime
import json
import logging
from operator import itemgetter
from os.path import isfile

import discord.ext.commands as commands

import utils.checks as checks
from utils.log import get_logger


def setup(bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(Timerboard(bot, 'fleetlist.json'))


class Timerboard:
    '''A cog defining commands for controlling the
    bot's timerboard functions'''

    def __init__(self, bot, fname):
        self.logger = get_logger(__name__, bot)
        self.bot = bot
        self.fname = fname

    def loadjson(self, jsonname):
        'A function which loads a json, given the filename'
        try:
            with open(jsonname) as data_file:
                data = json.load(data_file)
            self.logger.info('Json successfully loaded.')
            return data
        except FileNotFoundError:
            return {"fleets": []}

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
        fleets = self.loadjson(self.fname)['fleets']
        response = ""
        if announce:
            response += "@everyone\n"
        fleet = fleets[index]
        response += "**Fleet {}:**\n".format(index + 1)
        ftime = datetime.datetime.strptime(fleet["fleettime"],
                                           '%Y-%m-%dT%H:%M:%S')
        response += "```\nWhen: {}\n".format(ftime)
        response += "FC: {}\n".format(fleet["fc"])
        response += "Type: {}\n".format(fleet['fleettype'])
        response += "Doctrine: {}\n".format(fleet['doctrine'])
        response += "Formup: {}```\n".format(fleet['formup'])
        self.logger.info(response)
        return response

    def get_health(self):
        '''Returns a string describing the status of this cog'''
        if isfile(self.fname):
            return '\n  \u2714 {} exists'.format(self.fname)
        else:
            return '\n  \u2716 No fleetlist file found'

    @commands.command()
    @commands.check(checks.is_admin)
    async def addfleet(self, *args):
        '''Adds a fleet to the list of fleets in the json.
        Input fleets in the format
        "DD/MM/YYYY HH/MM FC FORMUP DOCTRINE FLEETTYPE'''
        if not args or len(args) != 6:
            if args:
                response = "You only entered {} argument(s)".format(len(args))
            else:
                response = "You didn't enter any arguments"
            response += ". Please ensure all of the 6 arguments are entered."
            await self.bot.say(response)
            return
        try:
            fleetdtime = datetime.datetime.strptime((args[0] + args[1]),
                                                    '%d/%m/%Y%H:%M')
        except ValueError:
            await self.bot.say("You entered an invalid date or time.")
            return
        self.logger.info('Converted to datetime')
        if fleetdtime <= datetime.datetime.now():
            await self.bot.say("Date entered is before the current date.")
            self.logger.warning("User entered an invalid date")
        else:
            fleetjson = self.loadjson(self.fname)
            fleetjson["fleets"].append({
                'fleettime': fleetdtime.isoformat(),
                'fc': args[2],
                'formup': args[3],
                'doctrine': args[4],
                'fleettype': args[5],
                'announced': False
            })
            self.savejson(fleetjson, self.fname)
            await self.bot.say("Fleet successfully added!")

    @commands.command()
    @commands.check(checks.is_admin)
    async def removefleet(self, number: int = 0):
        'Removes a fleet from the json via number on the list of fleets'
        fleetjson = self.loadjson(self.fname)
        if number > 0 and number <= len(fleetjson['fleets']):
            fleetjson['fleets'].pop(number - 1)
            self.savejson(fleetjson, self.fname)
            await self.bot.say("Fleet %d successfully removed." % number)
        else:
            await self.bot.say("You didn't enter a valid fleet number.")

    @commands.command()
    @commands.check(checks.is_admin)
    async def listfleets(self):
        'Lists all fleets to the chat in discord'
        fleets = self.loadjson(self.fname)['fleets']
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
    @commands.check(checks.is_admin)
    async def announcefleets(self):
        'Announces all un-announced fleets'
        fleetjson = self.loadjson(self.fname)
        n_fleets = len(fleetjson['fleets'])
        announced = False
        for idx in range(n_fleets):
            if not fleetjson['fleets'][idx]["announced"]:
                await self.bot.say(self.listfleet(idx, True))
                fleetjson['fleets'][idx]["announced"] = True
                self.savejson(fleetjson, self.fname)
                announced = True
        if not announced:
            await self.bot.say("All Fleets Announced!")

    @commands.command()
    @commands.check(checks.is_admin)
    async def resetannouncefleets(self, number: str = ''):
        '''Resets the boolean specifying whether a fleet has been announced.
        Enter a fleet number to reset a specific fleet or "all" to reset all'''
        fleetjson = self.loadjson(self.fname)
        n_fleets = len(fleetjson['fleets'])
        if number.isdecimal():
            number = int(number)
            if number > 0 and number <= n_fleets:
                fleetjson['fleets'][int(number) - 1]["announced"] = False
                self.savejson(fleetjson, self.fname)
                await self.bot.say(
                    "Fleet %s's announcement status reset." % number)
                self.logger.info('User reset fleet %s\'s announcement status',
                                 number)
                return
        elif number == '*' or number == 'all':
            for idx in range(n_fleets):
                fleetjson['fleets'][idx]["announced"] = False
            self.savejson(fleetjson, self.fname)
            await self.bot.say("All anouncement statuses reset.")
            self.logger.info('User reset all announcement statuses')
            return

        error = "Enter a valid fleet number to reset or * to reset all"
        await self.bot.say(error)
