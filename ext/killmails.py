'''
Killmail posting cog for antinub-gregbot project.

Monitors zKillboard's redisQ api and posts killmails relevant to your corp in
the given channel.
'''
from asyncio import sleep as async_sleep
import logging

import aiohttp
from discord.compat import create_task


def setup(bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(Killmails(bot))


class Killmails:
    '''A cog which monitors zKillboard's redisQ api and posts links to
    killmails which match the provided rule'''
    def __init__(self, bot):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.channel = self.bot.get_channel('244849123759489024')
        # self.corp_id = 98199571
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.corp_id = 98388312
        self.listening = False
        self.url = 'http://redisq.zkillboard.com/listen.php'
        self.start_listening()

    def get_status(self):
        'Returns a string describing the status of this cog'
        return 'Listening' if self.listening else 'Not listening'

    def is_relevant(self, package):
        'Returns true if the killmail should be relayed to discord'
        if package['killmail']['victim']['corporation']['id'] == self.corp_id:
            return True
        for attacker in package['killmail']['attackers']:
            if 'corporation' in attacker:
                if attacker['corporation']['id'] == self.corp_id:
                    return True
        return False

    async def handle_package(self, package):
        'Checks is_relevant to see if the killmail needs posting to discord'
        if package:
            if self.is_relevant(package):
                kill_id = package['killID']
                message = 'https://zkillboard.com/kill/{}/'.format(kill_id)
                await self.bot.send_message(self.channel, message)
                self.logger.info('Posted a killmail')
            else:
                self.logger.info('Ignored a killmail')
        else:
            self.logger.info('No kills retrieved')

    async def retrieve_kills(self):
        'Returns a dictionary containing the contents of the redisQ package'
        async with self.session.get(self.url) as response:
            assert response.status == 200
            zkb_data = await response.json()
            return zkb_data['package']

    async def listen_loop(self):
        '''Loops to try to retrieve killmail packages'''
        while self.listening:
            await async_sleep(3)
            try:
                package = await self.retrieve_kills()
                await self.handle_package(package)
            except Exception as exc:
                self.logger.error('%s: %s', type(exc), exc)
        self.session.close()

    def start_listening(self):
        'Starts the task of checking for new killmails every 5 minutes'
        self.listening = True
        create_task(self.listen_loop(), loop=self.bot.loop)

    def __unload(self):
        self.listening = False
        self.session.close()

# if __name__ == '__main__':
#     logging.basicConfig()
#     logging.getLogger().setLevel(logging.INFO)
#     with open('../test.json', 'rt') as data_json:
#         data_dict = json.load(data_json)
#     logger = logging.getLogger(__name__)
#     logger.info(data_dict['package']['zkb']['points'])
