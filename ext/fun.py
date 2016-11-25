'''
Meme cog made by Steveizi for antinub-gregbot project.

Contains several useless but fun commands
'''
import logging
from random import randint

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

    @commands.command()
    async def wopolusa(self):
        '''Posts a picture of Wopolusa to the chat'''
        await self.bot.say('http://i.imgur.com/wnwTGnf.png')

    @commands.command()
    async def stalin(self):
        '''Posts a picture describing Stalin\'s limit'''
        await self.bot.say('https://i.imgur.com/5ujkkrz.gifv')

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
