'''
Killmail posting cog for antinub-gregbot project.

Monitors zKillboard's redisQ api and posts killmails relevant to your corp in
the given channel.
'''
from asyncio import CancelledError, sleep
from datetime import datetime
from socket import AF_INET
import logging
from traceback import format_exception

from aiohttp import ClientResponseError, ClientSession, TCPConnector
from discord import Colour
from discord.embeds import Embed

from config import KILLMAILS
from utils.messaging import notify_owner, Paginate


class Killmails:
    '''A cog which monitors zKillboard's redisQ api and posts links to
    killmails which match the provided rule'''
    def __init__(self, bot, config):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.conf = config
        self.colours = {
            'green': Colour(0x007a00),
            'red': Colour(0x7a0000)
        }

        self.zkb_listener = None
        connector = TCPConnector(family=AF_INET if config['force_ipv4'] else 0)
        self.session = ClientSession(connector=connector)
        self.channel = self.bot.get_channel(self.conf['channel_id'])

        self.format_tracker = {'old': 0, 'total': 0}

        self.start_listening()

    def __unload(self):
        self.zkb_listener.cancel()

    def get_health(self):
        'Returns a string describing the status of this cog'
        if not self.zkb_listener.done():
            ret_string = '\n  \u2714 Listening {}% Old Format'
        else:
            ret_string = '\n  \u2716 Not listening {}% Old Format'
        old = self.format_tracker['old']
        total = self.format_tracker['total']
        percentage = 100 * old / max(total, 1)
        return ret_string.format(percentage)

    def start_listening(self, delay=0):
        'Start the listen loop and add the recovery callback'
        self.zkb_listener = self.bot.loop.create_task(
            self.retrieve_kills(delay))
        self.zkb_listener.add_done_callback(self.recover)

    async def retrieve_kills(self, delay):
        '''Loops to try to retrieve killmail packages'''
        await sleep(delay)
        try:
            while True:
                try:
                    package = await self.wait_for_package()
                except ClientResponseError:
                    self.logger.warning('Ignoring ClientResponseError')
                    continue

                if package:
                    self.bot.dispatch('killmail',
                                      await self.fetch_crest_info(package))
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
            exc_info = (type(exc), exc, exc.__traceback__)
            self.logger.error('An error occurred, restarting the loop',
                              exc_info=exc_info)
            self.bot.loop.create_task(self.error_to_admins(exc_info))
            self.start_listening(10)

    async def error_to_admins(self, exc_info):
        'Pass on the error which caused the loop to break to admins'
        message = 'Error in killmail retrieve loop:'
        paginate = Paginate(
            ''.join(format_exception(*exc_info)),
            enclose=('```Python\n', '```')
        )
        notification = [paginate.prefix_next(message)] + list(paginate)
        await notify_owner(self.bot, notification)

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

    async def on_killmail(self, package):
        'Test the killmail for relevancy and then send to discord or ignore'
        k_id = package['killID']
        try:
            if self.is_relevant(package):
                self.logger.info('Relaying killmail, ID: %s', k_id)
                embed = self.killmail_embed(package)
                msg = await self.bot.send_message(self.channel, embed=embed)
                if embed.colour == self.colours['red']:
                    await self.bot.add_reaction(msg, '\U0001F1EB')
            else:
                self.logger.debug('Ignoring killmail')
        except KeyError:
            self.logger.exception("Key Error")

    def is_relevant(self, package):
        'Returns True if a killmail should be relayed to discord'
        value = package['zkb']['totalValue'] / 1000000.0
        if value >= self.conf['others_value'] and self.conf['others_value']:
            return True

        self.format_tracker['total'] += 1
        try:
            killmail = package['killmail']
            old_format = False
        except KeyError:  # zkb pls
            killmail = package
            old_format = True
            self.format_tracker['old'] += 1

        if old_format:
            victim_corp = str(killmail['victim']['corporation']['id'])
        else:
            victim_corp = str(killmail['victim']['corporation_id'])
        if victim_corp in self.conf['corp_ids']:
            if value >= self.conf['corp_ids'][victim_corp]:
                return True

        for attacker in killmail['attackers']:
            if 'corporation' in attacker:
                if old_format:
                    attacker_corp = str(attacker['corporation']['id'])
                else:
                    attacker_corp = str(attacker['corporation_id'])
                if attacker_corp in self.conf['corp_ids']:
                    if value >= self.conf['corp_ids'][attacker_corp]:
                        return True

        return False

    async def fetch_crest_info(self, package):
        'Fills in potentially missing information from CREST api'
        zkb = package['zkb']  # The zkb specific part of the package
        url = 'https://crest-tq.eveonline.com/killmails/{}/{}/'.format(
            package['killID'],
            zkb['hash']
        )
        async with self.session.get(url) as resp:
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
            embed.colour = self.colours['red']
        else:
            embed.colour = self.colours['green']
        embed.set_thumbnail(url=('http://imageserver.eveonline.com/Type/'
                                 '{}_64.png').format(ship['id_str']))
        return embed


def setup(bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(Killmails(bot, KILLMAILS))
