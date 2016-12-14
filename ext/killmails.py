'''
Killmail posting cog for antinub-gregbot project.

Monitors zKillboard's redisQ api and posts killmails relevant to your corp in
the given channel.
'''
import asyncio
from datetime import datetime
import logging

import aiohttp
from discord.embeds import Embed

from config import KILLMAILS, OWNER_ID


class Killmails:
    '''A cog which monitors zKillboard's redisQ api and posts links to
    killmails which match the provided rule'''
    def __init__(self, bot, config):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.conf = config

        self.session = aiohttp.ClientSession()
        self.channel = self.bot.get_channel(self.conf['channel_id'])

        self.zkb_listener = self.bot.loop.create_task(self.retrieve_kills())
        self.zkb_listener.add_done_callback(self.handle_exception)

    def __unload(self):
        self.zkb_listener.cancel()

    def get_health(self):
        'Returns a string describing the status of this cog'
        if not self.zkb_listener.done():
            return '\n  \u2714 Listening'
        else:
            return '\n  \u2716 Not listening'

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
        except asyncio.CancelledError:
            pass
        finally:
            await self.session.close()

    def handle_exception(self, fut):
        'Make sure any exception from the future is consumed'
        exc = fut.exception()
        if exc:
            self.logger.exception(exc)
            chan = self.bot.get_user_info(OWNER_ID)
            self.bot.loop.create_task(
                self.bot.send_message(chan, '`{}`'.format(exc)))

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

        victim_corp_id = package['killmail']['victim']['corporation']['id']
        if str(victim_corp_id) in self.conf['corp_ids']:
            if value >= self.conf['corp_ids'][victim_corp_id]:
                return True

        for attacker in package['killmail']['attackers']:
            if 'corporation' in attacker:
                attacker_corp_id = attacker['corporation']['id']
                if str(attacker_corp_id) in self.conf['corp_ids']:
                    if value >= self.conf['corp_ids'][attacker_corp_id]:
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
