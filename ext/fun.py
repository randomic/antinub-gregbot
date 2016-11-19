import logging
import config
from random import randint
import discord

import discord.ext.commands as commands


def setup(bot):
    bot.add_cog(Fun(bot))


# Helper functions
def isOwner(context):
    'Check whether or not the user is the owner of the bot'
    return context.message.author.id == config.OWNER_ID


class Fun:
    '''A cog defining meme commands'''
    def __init__(self, bot):
        self.logger = logging.getLogger(__name__)

        self.bot = bot

    @commands.command()
    async def wopolusa(self):
        '''Posts a picture of Wopolusa to the chat'''
        await self.bot.say('http://i.imgur.com/wnwTGnf.png')

    @commands.command()
    async def stalin(self):
        '''Posts a picture describing Stalin\'s limit'''
        await self.bot.say('https://i.imgur.com/5ujkkrz.gif')

    @commands.command()
    @commands.check(isOwner)
    async def initguess(self, MAX : str):
        '''Randomly generates a number from 0-MAX and
        allows the user to guess the number'''
        if MAX.isnumeric():
            MAX = int(MAX)
            self.randnumber = randint(0,MAX)
            self.logger.info('Random number generated: %d', self.randnumber)
            await self.bot.say('Random number generated between 0 and %d!\nUse "!guess" to try and guess it!' % MAX)
        else:
            self.logger.warning('User entered invalid MAX number')
            await self.bot.say('You entered an invalid max number. Make sure it\'s only numbers!')

    @commands.command()
    async def guess(self, GUESS : str):
        '''Allows the user to guess the number generated
        in the !initguess command'''
        if GUESS.isnumeric():
            GUESS = int(GUESS)
            if GUESS == self.randnumber:
                self.logger.info('User guessed correct number')
                await self.bot.say('You guessed correctly! The number was %d' % self.randnumber)
            else:
                self.logger.info('User guessed incorrect number')
                difference = self.randnumber - GUESS
                if difference > 0:
                    await self.bot.say('You guessed too low! Try again.')
                else:
                    await self.bot.say('You guessed too High! Try again.')
        else:
            self.logger.warning('User entered an invalid guess')
            await self.bot.say('You entered an invalid guess. Make sure it\'s only numbers!')