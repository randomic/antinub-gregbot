import logging
import config
import asyncio

from slixmpp import ClientXMPP
import discord.ext.commands as commands


def setup(bot):
    bot.add_cog(Jabber(bot, config.JABBER_SERVERS))


class Jabber:
    '''A cog which connects to config defined xmpp
    servers and relays messages from certain senders
    to the config defined channel.'''
    def __init__(self, bot, jabberServers):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.jabberServers = jabberServers
        self.xmppRelays = []

    async def on_ready(self):
        for server in self.jabberServers:
            self.xmppRelays.append( XmppRelay(self.bot, server) )


class XmppRelay(ClientXMPP):
    '''Connects to an XMPP server and relays broadcasts
    to a specified discord channel'''
    def __init__(self, bot, jabberDetails):
        self.logger = logging.getLogger(__name__)
        self.bot = bot

        ClientXMPP.__init__(self, jabberDetails['jabber_id'], jabberDetails['password'])

        self.relay_from = jabberDetails['relay_from']
        self.channel = self.bot.get_channel(jabberDetails['channel'])      

        self.add_event_handler('session_start', self.start)
        if self.connect():
            self.process()
        
        self.add_event_handler('message', self.message)

    def start(self, event):
        self.send_presence(ptype='away')
        self.get_roster()

    async def message(self, msg):
        sender = msg['from'].bare
        if sender == self.relay_from:
            self.logger.info('Relaying message from %s', sender)
            r_message = '```@everyone BROADCAST FROM: {}\n\n{}```'.format(sender, msg['body'])
            await self.bot.send_message(self.channel, r_message)
        else:
            self.logger.info('Ignored message from %s', sender)