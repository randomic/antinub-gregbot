'''
Antispam cog made by Steveizi for antinub-gregbot project.

'''
import logging
from asyncio import sleep


def setup(bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(Antispam(bot))


class Antispam:
    '''A cog handling anti-spam'''
    def __init__(self, bot):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.convicts = {}
        self.past_convicts = {}
        self.loop_number = 0

        self.start_antispam(15)

    async def on_message(self, msg):
        '''A function handling messages sent by users in the presence of the
        bot'''
        if self.mentioncheck(msg):
            self.handleconvict(int(msg.author.id))
        print(self.convicts)

    def mentioncheck(self, msg):
        '''A function taking a message and returning a bool if any
        sort of mention was used in it'''
        if msg.mention_everyone:
            return True
        elif len(msg.mentions) or len(msg.role_mentions):
            return True
        else:
            return False

    def handleconvict(self, userid):
        '''A coroutine handling each message with a mention in, adding the
        user who sent the message to a list'''
        if userid in self.convicts:
            self.convicts[userid] += 1
        else:
            self.convicts[userid] = 1

    def start_antispam(self, delay=15):
        '''A coroutine starting the antispam loop'''
        self.logger.info("Loop started.")
        self.antispamloop = self.bot.loop.create_task(self.check_spam(delay))
        self.antispamloop.add_done_callback(self.recover)

    async def check_spam(self, delay):
        '''A coroutine handling the data brought in from the mentions in
        messages'''
        while True:
            await sleep(delay)
            self.logger.info("Loop at #%d" % self.loop_number)
            self.loop_number += 1
            convictlist = self.comparespam()
            if convictlist:
                await self.remove_kebab(convictlist)
            else:
                for key in self.convicts:
                    if self.convicts[key] > 10:
                        convictlist.append(key)
                await self.remove_kebab(convictlist)

            self.past_convicts = self.convicts

            if self.loop_number == 4:
                self.loop_number = 0
                self.convicts = {}

    def comparespam(self):
        '''A function checking if the difference between the last check and
        the new check is greater than 3, returning their userID if so'''
        convictlist = []
        self.logger.info("Comparing spam")
        for key in self.convicts:
            if key in self.past_convicts:
                difference = (self.convicts[key]-self.past_convicts[key])
                if difference > 4:
                    convictlist.append(self.convicts[key])
        return convictlist

    async def remove_kebab(self, convictlist):
        '''A function removing the kebab from the premises'''
        self.logger.info("Removing kebab for")
        self.logger.info(convictlist)
        for userid in convictlist:
            user = await self.bot.get_user_info(userid)
            await self.bot.remove_roles(user, user.top_role)

    def recover(self, fut):
        'The loop should not break unless cancelled so restart the loop'
        self.antispamloop = None
        if not fut.cancelled():
            exc = fut.exception()
            exc_info = (type(exc), exc, exc.__traceback__)
            self.logger.error('An error occurred, restarting the loop',
                              exc_info=exc_info)
            self.start_antispam(15)
