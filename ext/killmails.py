'''
Killmail posting cog for antinub-gregbot project.

Monitors zKillboard's redisQ api and posts killmails relevant to your corp in
the given channel.
'''
import asyncio
from datetime import datetime
import logging

from aiohttp import ClientError
from discord.compat import create_task
from discord.embeds import Embed

from config import KILLMAILS, OWNER_ID
from utils.control import paginate


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
        # self.corp_id = 98388312
        self.listening = False
        self.url = KILLMAILS['redisQ_url']

        self.corp_ids = KILLMAILS['corp_ids']
        self.others_value = KILLMAILS['others_value']

        self.start_listening()

    def get_health(self):
        'Returns a string describing the status of this cog'
        if self.listening:
            return '\n  \u2714 Listening'
        else:
            return '\n  \u2716 Not listening'

    def is_relevant(self, package):
        'Returns True if a killmail should be relayed to discord'
        value = package['zkb']['totalValue'] / 1000000.0
        if value >= self.others_value and self.others_value:
            return True

        victim_corp_id = package['killmail']['victim']['corporation']['id_str']
        if victim_corp_id in self.corp_ids:
            if value >= self.corp_ids[victim_corp_id]:
                return True

        for attacker in package['killmail']['attackers']:
            if 'corporation' in attacker:
                attacker_corp_id = attacker['corporation']['id_str']
                if attacker_corp_id in self.corp_ids:
                    if value >= self.corp_ids[attacker_corp_id]:
                        return True

        return False

    def killmail_embed(self, package):
        'Generates the embed which the killmail will be posted in'
        victim = package['killmail']['victim']
        ship = victim['shipType']
        embed = Embed()

        embed.title = '{} | {} | {}'.format(
            package['killmail']['solarSystem']['name'],
            ship['name'],
            victim['character']['name'])

        embed.description = ('{} ({}) lost their {} in {}\n'
                             'Total Value: {:,} ISK\n'
                             '\u200b').format(
                                 victim['character']['name'],
                                 victim['corporation']['name'],
                                 ship['name'],
                                 package['killmail']['solarSystem']['name'],
                                 package['zkb']['totalValue'])
        embed.url = 'https://zkillboard.com/kill/{}/'.format(package['killID'])
        embed.timestamp = datetime.strptime(package['killmail']['killTime'],
                                            '%Y.%m.%d %H:%M:%S')
        if victim['corporation']['id_str'] in self.corp_ids:
            embed.colour = 0x7a0000  # red
        else:
            embed.colour = 0x007a00  # green
        embed.set_thumbnail(url=('http://imageserver.eveonline.com/Type/'
                                 '{}_64.png').format(ship['id_str']))
        return embed

    async def handle_package(self, package):
        'Checks is_relevant to see if the killmail needs posting to discord'
        if package:
            try:
                rel = self.is_relevant(package)
            except KeyError as exc:
                self.logger.warning(exc)
                msgs = paginate('<@{}>\n{}'.format(OWNER_ID, str(package)))
                for msg in msgs:
                    await self.bot.send_message(self.channel, msg)
                rel = False
            if rel:
                embed = self.killmail_embed(package)
                await self.bot.send_message(self.channel, embed=embed)
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
                await asyncio.sleep(0.5)
            except (AssertionError, ClientError, asyncio.TimeoutError) as exc:
                self.logger.exception(exc)
        self.logger.info('Loop done')

    def start_listening(self):
        'Starts the task of checking for new killmails'
        self.listening = True
        create_task(self._run_listen_loop())

    def __unload(self):
        self.listening = False
