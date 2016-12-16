'''
Killmail posting cog for antinub-gregbot project.

Monitors zKillboard's redisQ api and posts killmails relevant to your corp in
the given channel.
'''
from asyncio import CancelledError
from datetime import datetime
import logging

from aiohttp import ClientSession
from discord.embeds import Embed

from config import KILLMAILS


class Killmails:
    '''A cog which monitors zKillboard's redisQ api and posts links to
    killmails which match the provided rule'''
    def __init__(self, bot, config):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.conf = config

        self.zkb_listener = None
        self.session = ClientSession()
        self.channel = self.bot.get_channel(self.conf['channel_id'])

        self.start_listening()

    def __unload(self):
        self.zkb_listener.cancel()

    def get_health(self):
        'Returns a string describing the status of this cog'
        if not self.zkb_listener.done():
            return '\n  \u2714 Listening'
        else:
            return '\n  \u2716 Not listening'

    def start_listening(self):
        'Start the listen loop and add the recovery callback'
        self.zkb_listener = self.bot.loop.create_task(self.retrieve_kills())
        self.zkb_listener.add_done_callback(self.recover)

    async def retrieve_kills(self):
        '''Loops to try to retrieve killmail packages'''
        try:
            while True:
                package = await self.wait_for_package()
                if package:
                    if self.is_relevant(package):
                        k_id = package['killID']
                        self.logger.info('Relaying killmail, ID: %s', k_id)
                        crest_package = await self.fetch_crest_info(package)
                        embed = self.killmail_embed(crest_package)
                        await self.bot.send_message(self.channel, embed=embed)
                    else:
                        self.logger.debug('Ignoring killmail')
                else:
                    self.logger.debug('Got empty package')
        except CancelledError:
            await self.session.close()
            raise CancelledError

    def recover(self, fut):
        'The loop should not break unless cancelled so restart the loop'
        self.zkb_listener = None
        if not fut.cancelled():
            exc = fut.exception()
            self.logger.exception(exc)
            self.logger.error('An error occurred, restarting the loop')
            self.start_listening()

    async def wait_for_package(self):
        'Returns a dictionary containing the contents of the redisQ package'
        async with self.session.get(self.conf['redisQ_url']) as resp:
            if resp.status == 200:
                zkb_data = await resp.json()
                return zkb_data['package']
            elif resp.status == 502:
                self.logger.info('redisQ is taking too long to respond')
            else:
                self.logger.error('redisQ: %s error occurred', resp.status)

    def is_relevant(self, package):
        'Returns True if a killmail should be relayed to discord'
        value = package['zkb']['totalValue'] / 1000000.0
        if value >= self.conf['others_value'] and self.conf['others_value']:
            return True

        victim_corp = str(package['killmail']['victim']['corporation']['id'])
        if victim_corp in self.conf['corp_ids']:
            if value >= self.conf['corp_ids'][victim_corp]:
                return True

        for attacker in package['killmail']['attackers']:
            if 'corporation' in attacker:
                attacker_corp = str(attacker['corporation']['id'])
                if attacker_corp in self.conf['corp_ids']:
                    if value >= self.conf['corp_ids'][attacker_corp]:
                        return True

        return False

    async def fetch_crest_info(self, package):
        'Fills in potentially missing information from CREST api'
        zkb = package['zkb']  # The zkb specific part of the package
        async with self.session.get(zkb['href']) as resp:
            if resp.status == 200:
                crest_data = await resp.json()
                crest_data['zkb'] = zkb
                return crest_data
            elif resp.status == 502:
                self.logger.info('CREST is taking too long to respond')
            else:
                self.logger.error('CREST: %s error occurred', resp.status)

    def killmail_embed(self, package):
        'Generates the embed which the killmail will be posted in'
        victim = package['victim']
        if 'character' in victim:
            victim_str = '{} ({})'.format(
                victim['character']['name'],
                victim['corporation']['name'])
        else:
            victim_str = victim['corporation']['name']
        ship = victim['shipType']

        embed = Embed()
        embed.title = '{} | {} | {}'.format(
            package['solarSystem']['name'],
            ship['name'],
            victim['corporation']['name'])
        embed.description = ('{} lost their {} in {}\n'
                             'Total Value: {:,} ISK\n'
                             '\u200b').format(
                                 victim_str,
                                 ship['name'],
                                 package['solarSystem']['name'],
                                 package['zkb']['totalValue'])
        embed.url = 'https://zkillboard.com/kill/{}/'.format(package['killID'])
        embed.timestamp = datetime.strptime(package['killTime'],
                                            '%Y.%m.%d %H:%M:%S')
        if victim['corporation']['id_str'] in self.conf['corp_ids']:
            embed.colour = 0x7a0000  # red
        else:
            embed.colour = 0x007a00  # green
        embed.set_thumbnail(url=('http://imageserver.eveonline.com/Type/'
                                 '{}_64.png').format(ship['id_str']))
        return embed


def setup(bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(Killmails(bot, KILLMAILS))
