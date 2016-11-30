'''
Meme cog made by Steveizi for antinub-gregbot project.

Contains several useless but fun commands
'''
import logging
from random import randint
import json
from os.path import isfile
import ext.permcheck as permcheck

import discord.ext.commands as commands


def setup(bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(Fun(bot))


class Fun:
    '''A cog defining meme commands'''
    def __init__(self, bot):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.guess_number = 0
        self.guess_max = 0
        self.memelist = ""

    def loadjson(self, jsonname):
        'A function which loads a json, given the filename'
        try:
            with open(jsonname) as data_file:
                data = json.load(data_file)
            self.logger.info('Json successfully loaded.')
            return data
        except FileNotFoundError:
            return {
                "memes": {}
            }

    def savejson(self, data, jsonname):
        'A function which saves a json, given the filename'
        try:
            with open(jsonname, 'wt') as outfile:
                json.dump(data, outfile)
            self.logger.info('Json successfully saved.')
        except TypeError as error:
            self.logger.error(error)

    def get_status(self):
        'Returns a string describing the status of this cog'
        response = ""
        if isfile('memes.json'):
            response += '\n  \u2714 memes.json exists, memes != dreams'
        else:
            response += '\n  \u2716 No meme file found'
        if self.guess_number:
            response += '\n  \u2714 Guessing game currently active'
        else:
            response += '\n  \u2716 No guessing game currently active'
        return response

    @commands.command()
    @permcheck.one()
    async def meme(self, memename: str, imglink: str=""):
        '''Posts a saved imgur link via a specified name
        or saves an imgur link to file under the name.
        Converts all memenames to lower case'''
        self.memelist = self.loadjson('memes.json')
        memename = memename.lower()
        if memename in self.memelist['memes'].keys():
            if imglink != "":
                await self.bot.say("Meme '%s' already exists!" % memename)
                self.logger.info("User tried to overwrite a meme")
            else:
                await self.bot.say(self.memelist['memes'].get(memename))
                self.logger.info('User posted %s to the chat', memename)
        elif imglink != "":
            self.memelist['memes'][memename] = imglink
            self.savejson(self.memelist, 'memes.json')
            await self.bot.say('`{}` added as `{}`!'.format(imglink, memename))
        else:
            await self.bot.say('You entered an invalid meme name')
            self.logger.warning('User entered an invalid meme name')

    @commands.command()
    @permcheck.one()
    async def removememe(self, memename: str):
        '''Removes a meme from file via the specific memename'''
        self.memelist = self.loadjson('memes.json')
        memename = memename.lower()
        if memename in self.memelist['memes'].keys():
            del self.memelist['memes'][memename]
            self.logger.info('User removed %s from memes.json', memename)
            await self.bot.say('%s removed from the memelist.' % memename)
            self.savejson(self.memelist, 'memes.json')
        else:
            self.logger.warning('User entered invalid memename "%s"', memename)
            await self.bot.say('You entered an invalid memename.')

    @commands.command()
    @permcheck.one()
    async def listmemes(self):
        '''Posts a list of the current memes available in the file'''
        memelist = self.loadjson('memes.json')['memes']
        response = "**Memes:**\n```"
        for key in sorted(memelist.keys()):
            response += "{}:\n  {}\n".format(key, memelist[key])
        response += "```"
        await self.bot.say(response)

    @commands.command(pass_context=True)
    async def guess(self, ctx, guess: int=0):
        '''Allows the user to guess a number. If there is no number to guess a
        new game is started'''
        if self.guess_number:
            if guess < 1 or guess > self.guess_max:
                await self.bot.delete_message(ctx.message)
            elif guess == self.guess_number:
                await self.bot.say('{} is correct! {} wins!'
                                   .format(guess, ctx.message.author.mention))
                self.guess_number = 0
            elif guess < self.guess_number:
                await self.bot.say('{} is too low! Guess again!'
                                   .format(guess))
                await self.bot.delete_message(ctx.message)
            else:
                await self.bot.say('{} is too high! Guess again!'
                                   .format(guess))
                await self.bot.delete_message(ctx.message)
        else:
            if guess < 1:
                guess = 1000
            self.guess_number = randint(1, guess)
            self.logger.info('New game started from 1-%s. The number is %s.',
                             guess, self.guess_number)
            self.guess_max = guess
            await self.bot.say('New game started! Guess the number '
                               + 'between 1 and {}'.format(guess))

    @commands.command()
    @permcheck.two()
    async def emoji(self, emoji: str, number: int=1):
        'Converts a string to :string: aka an emoji'
        emoji = ":" + emoji + ":"
        await self.bot.say((emoji*number))

    @commands.command()
    async def lmgtfy(self, *args):
        'Googles the input for the mentally impaired'
        response = "https://lmgtfy.com/?q="
        count = 0
        for arg in args:
            if count != 0:
                response += "+"
            response += arg
            count += 1
        await self.bot.say(response)
        self.logger.info('User posted a lmgtfy to the chat.')
