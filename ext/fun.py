'''
Meme cog made by Steveizi for antinub-gregbot project.

Contains several useless but fun commands
'''
import logging
from random import randint
import json

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
                "memes": []
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
    async def meme(self, memename: str, imglink: str=""):
        '''Posts a saved imgur link via a specified name
        or saves an imgur link to file under the name'''
        self.memelist = self.loadjson('memes.json')
        if any(memename in x for x in self.memelist['memes']):
            self.logger.info('KappaPride')
            self.logger.info(self.memelist['memes'][memename])
            await self.bot.say(self.memelist['memes'][memename].get(memename))
            self.logger.info('User posted %s to the chat', memename)
        elif imglink != "":
            self.memelist['memes'].append({
                memename: imglink
            })
            self.savejson(self.memelist, 'memes.json')
            await self.bot.say('"{}" added as {}!'.format(imglink, memename))
        else:
            await self.bot.say('You entered an invalid meme name')
            self.logger.warning('User entered an invalid meme name')

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
            self.guess_max = guess
            await self.bot.say('New game started! Guess the number '
                               + 'between 1 and {}'.format(guess))
