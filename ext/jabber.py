'''
Jabber relay cog made for antinub-gregbot project.

When added to a bot it creates an xmpp client per one configured in
config.JABBER_SERVERS
It will then listen on those servers and relay any messages received if
they are sent by a jid in the config.JABBER_SERVERS['relay_from'] list
'''
import logging

from slixmpp import ClientXMPP

import config


def setup(bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(Jabber(bot, config.JABBER_SERVERS))


class Jabber:
    '''A cog which connects to config defined xmpp servers and relays messages
    from certain senders to the config defined channel'''
    def __init__(self, bot, xmpp_servers):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.xmpp_servers = xmpp_servers
        self.xmpp_relays = []

    async def on_ready(self):
        'Waits for the discord bot to be ready before creating jabber clients'
        for server in self.xmpp_servers:
            self.xmpp_relays.append(XmppRelay(self.bot, server))

    def get_status(self):
        'Returns a string describing the status of this cog'
        if self.xmpp_relays:
            response = ''
            for xmpp_relay in self.xmpp_relays:
                response += '\n{}: '.format(xmpp_relay.server)
                online = xmpp_relay.is_connected()
                response += 'Connected' if online else 'Disconnected'
        else:
            response = 'No relays initialised'
        return response


class XmppRelay(ClientXMPP):
    '''Connects to an XMPP server and relays broadcasts
    to a specified discord channel'''
    def __init__(self, bot, jabber_server):
        ClientXMPP.__init__(self,
                            jabber_server['jabber_id'],
                            jabber_server['password'])

        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.relay_from = jabber_server['relay_from']
        self.channel = self.bot.get_channel(jabber_server['channel'])

        self.add_event_handler('session_start', self.start)
        if self.connect():
            self.process()

        self.add_event_handler('message', self.message)

    def start(self, dummy_event):
        'Follow standard xmpp protocol after connecting to the server'
        self.send_presence(ptype='away')
        self.get_roster()

    async def message(self, msg):
        'Relay messages from specified senders to specified discord channel'
        sender = msg['from'].bare
        if sender in self.relay_from:
            self.logger.info('Relaying message from %s', sender)
            r_message = '@everyone\n```{}```'.format(msg['body'])
            await self.bot.send_message(self.channel, r_message)
        else:
            self.logger.info('Ignored message from %s', sender)
