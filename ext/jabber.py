'''
Jabber relay cog made for antinub-gregbot project.

When added to a bot it creates an xmpp client per one configured in
config.JABBER_SERVERS
It will then listen on those servers and relay any messages received if
they are sent by a jid in the config.JABBER_SERVERS['relay_from'] list
'''
import logging

from slixmpp import ClientXMPP

from config import JABBER


def setup(bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(Jabber(bot, JABBER))


class Jabber:
    '''A cog which connects to config defined xmpp servers and relays messages
    from certain senders to the config defined channel'''
    def __init__(self, bot, config):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.channel = self.bot.get_channel(config['channel'])
        self.xmpp_relays = []
        self.last_msg = None

        self.create_clients(config['servers'])

    def create_clients(self, xmpp_servers):
        'Creates an XmppRelay client for each server specified'
        for server in xmpp_servers:
            self.xmpp_relays.append(XmppRelay(self, server))

    def get_health(self):
        'Returns a string describing the status of this cog'
        if self.xmpp_relays:
            response = ''
            for xmpp_relay in self.xmpp_relays:
                if xmpp_relay.is_connected():
                    resp = '\n  \u2714 {} - Connected'
                else:
                    resp = '\n  \u2716 {} - Disconnected'
                response += resp.format(xmpp_relay.boundjid.host)
        else:
            response = '\n  \u2716 No relays initialised'
        return response

    async def relay_message(self, msg):
        'Relay message to discord, ignore if it is a duplicate'
        body = msg['body']
        idx = body.rfind('Broadcast sent at ')
        raw_msg = body[:idx] if idx > 0 else body

        if raw_msg != self.last_msg:
            self.last_msg = raw_msg
            self.logger.info('Relaying message from %s', msg['from'].bare)
            r_message = '@everyone\n```\n{}```'.format(msg['body'])
            await self.bot.send_message(self.channel, r_message)
        else:
            self.logger.info('Ignored duplicate message from %s',
                             msg['from'].bare)

    def __unload(self):
        for xmpp_relay in self.xmpp_relays:
            xmpp_relay.disconnect()


class XmppRelay(ClientXMPP):
    '''Connects to an XMPP server and relays broadcasts
    to a specified discord channel'''
    def __init__(self, cog, jabber_server):
        ClientXMPP.__init__(self,
                            jabber_server['jabber_id'],
                            jabber_server['password'])

        self.logger = cog.logger
        self.cog = cog
        self.relay_from = jabber_server['relay_from']

        self.add_event_handler('session_start', self.session_start)
        self.add_event_handler('message', self.message)

        if self.connect():
            self.process()

    def session_start(self, dummy_event=None):
        'Follow standard xmpp protocol after connecting to the server'
        self.send_presence(ptype='away')
        self.get_roster()

    async def message(self, msg):
        'Pass messages from specified senders to the cog for relaying'
        if msg['type'] == 'chat':
            sender = msg['from'].bare
            if sender in self.relay_from:
                await self.cog.relay_message(msg)
            else:
                self.logger.info('Ignored message from %s', sender)
        else:
            self.logger.info('Ignored message of type %s', msg['type'])
