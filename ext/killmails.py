'''
Killmail posting cog for antinub-gregbot project.

Monitors zKillboard's redisQ api and posts killmails relevant to your corp in
the given channel.
'''
from asyncio import sleep
import logging

import ext.permcheck as permcheck
import discord.ext.commands as commands

from aiohttp import ClientError
from discord.compat import create_task

from config import KILLMAILS


def setup(bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(Killmails(bot))


class Killmails:
    '''A cog which monitors zKillboard's redisQ api and posts links to
    killmails which match the provided rule'''
    def __init__(self, bot):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.channel = self.bot.get_channel(KILLMAILS['channel_id'])
        self.corp_id = KILLMAILS['corp_id']
        # self.corp_id = 98388312
        self.url = KILLMAILS['redisQ_uri']
        if 'is_relevant' in KILLMAILS:
            self.is_relevant = KILLMAILS['is_relevant']
        else:
            self.is_relevant = self._default_is_relevant
        self.listening = False

        self.start_listening()

    def get_status(self):
    def get_health(self):
        'Returns a string describing the status of this cog'
        if self.listening:
            return '\n  \u2714 Listening for corp id: {}'.format(self.corp_id)
        else:
            return '\n  \u2716 Not listening'

    def _default_is_relevant(self, package):
        'Returns true if the killmail should be relayed to discord'
        victim_corp = package['killmail']['victim']['corporation']
        if victim_corp['id'] == self.corp_id:
            return '{} loss'.format(victim_corp['name'])
        for attacker in package['killmail']['attackers']:
            if 'corporation' in attacker:
                if attacker['corporation']['id'] == self.corp_id:
                    return '{} kill'.format(attacker['corporation']['name'])
        return ''

    async def handle_package(self, package):
        'Checks is_relevant to see if the killmail needs posting to discord'
        if package:
            relevancy_string = self.is_relevant(package)
            if relevancy_string:
                kill_id = package['killID']
                message = '**{}**\n  '.format(relevancy_string)
                message += 'https://zkillboard.com/kill/{}/'.format(kill_id)
                await self.bot.send_message(self.channel, message)
                self.logger.info('Posted a killmail')
            else:
                self.logger.debug('Ignored a killmail')
        else:
            self.logger.debug('No kills retrieved')

    async def retrieve_kills(self):
        'Returns a dictionary containing the contents of the redisQ package'
        async with self.bot.http.session.get(self.url) as response:
            assert response.status == 200
            zkb_data = await response.json()
            return zkb_data['package']

    async def _run_listen_loop(self):
        '''Loops to try to retrieve killmail packages'''
        while self.listening:
            try:
                package = await self.retrieve_kills()
                await self.handle_package(package)
                await sleep(0.25)
            except AssertionError as exc:
                self.logger.exception(exc)
            except ClientError as exc:
                self.logger.exception(exc)
        self.logger.info('Loop exited')

    def start_listening(self):
        'Starts the task of checking for new killmails'
        self.listening = True
        create_task(self._run_listen_loop())

    def __unload(self):
        self.listening = False

    @commands.group(pass_context=True)
    @permcheck.four()
    async def killmails(self, ctx):
        '''Group of commands regarding stopping and starting
        of killmail scraping'''
        if ctx.invoked_subcommand is None:
            await self.bot.say(self.bot.extensions.keys())

    async def start(self):
        'Attempts to start the task of checking for new killmails'
        self.start_listening

    async def stop(self):
        'Stops the task of checking for new killmails'
        self.listening = False
