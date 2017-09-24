'''
Jabber relay cog made for antinub-gregbot project.

When added to a bot it creates an xmpp client per one configured in
config.JABBER_SERVERS
It will then listen on those servers and relay any messages received if
they are sent by a jid in the config.JABBER_SERVERS['relay_from'] list
'''
import logging
from datetime import datetime

import aioxmpp

from utils.messaging import paginate
from config import JABBER
from discord.embeds import Embed


def setup(bot):
    'Adds the cog to the provided discord bot'
    bot.add_cog(Jabber(bot, JABBER))


class Jabber:
    '''A cog which connects to config defined xmpp servers and relays messages
    from certain senders to the config defined channel'''
    def __init__(self, bot, config):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.xmpp_relays = []
        self.last_msg = None

        self.create_clients(config['servers'])

    def create_clients(self, xmpp_servers):
        'Creates an XmppRelay client for each server specified'
        for server in xmpp_servers:
            self.xmpp_relays.append(XmppRelay(self, server, self.logger))

    def get_health(self):
        'Returns a string describing the status of this cog'
        if self.xmpp_relays:
            response = ''
            for xmpp_relay in self.xmpp_relays:
                if xmpp_relay.established:
                    resp = '\n  \u2714 {} - Connected'
                else:
                    resp = '\n  \u2716 {} - Disconnected'
                response += resp.format(xmpp_relay.local_jid)
        else:
            response = '\n  \u2716 No relays initialised'
        return response

    async def on_broadcast(self, package):
        'Relay message to discord, ignore if it is a duplicate'
        body = package['msg']['body']

        idx = body.rfind('Broadcast sent at ')
        raw_msg = body[:idx] if idx > 0 else body

        if raw_msg != self.last_msg:
            self.last_msg = raw_msg
            self.logger.info('Relaying message from %s',
                             package['msg']['from'].bare)
            r_message = paginate(package['msg']['body'], aff='', pref='',
                                 max_length=1900)
            pref = package['prefix'] if package['prefix'] else None
            for page in r_message:
                if r_message.index(page):
                    pref = None
                embed = self.ping_embed(package, page, r_message)
                for channelid in package['forward_to']:
                    channel = self.bot.get_channel(channelid)
                    await self.bot.send_message(channel, embed=embed,
                                                content=pref)
        else:
            self.logger.info('Ignored duplicate message from %s',
                             package['msg']['from'].bare)

    def ping_embed(self, package, message, r_message):
        'Formats and generates the embed for the ping'
        embed = Embed()
        totalmsgs = len(r_message)
        currentmsg = r_message.index(message)

        if not currentmsg:
            embed.title = package['msg']['from'].bare
            embed.set_author(name=package['description'])

        embed.description = message
        embed.set_thumbnail(url=package['logo_url'])
        embed.set_footer(text='Message {}/{}'.format(currentmsg+1, totalmsgs))
        embed.timestamp = datetime.now()

        return embed

    def __unload(self):
        for xmpp_relay in self.xmpp_relays:
            xmpp_relay.disconnect()


class XmppRelay(aioxmpp.PresenceManagedClient):
    '''Connects to an XMPP server and relays broadcasts
    to a specified discord channel'''
    def __init__(self, cog, jabber_server, logger):
        super(XmppRelay, self).__init__(
            self,
            jabber_server['jabber_id'],
            aioxmpp.make_security_layer(jabber_server['password']),
            logger=logger
        )

        self.bot = cog.bot
        self.relay_from = jabber_server['relay_from']
        self.jabber_server = jabber_server

        self.stream.register_message_callback(
            aioxmpp.MessageType.CHAT,
            None,
            self.message_receieved
        )

        self.presence = aioxmpp.PresenceState(True, 'away')

    def message_receieved(self, msg):
        'Pass messages from specified senders to the cog for relaying'
        if msg.type == aioxmpp.MessageType.CHAT:
            sender = msg['from'].bare
            if sender in self.relay_from:
                package = {
                    "msg": msg,
                    "forward_to": self.jabber_server['forward_to'],
                    "description": self.jabber_server['description'],
                    "prefix": self.jabber_server['prefix'],
                    "logo_url": self.jabber_server['logo_url']
                    }
                self.bot.dispatch('broadcast', package)
            else:
                self.logger.info('Ignored message from %s', sender)
        else:
            self.logger.info('Ignored message of type %s', msg.type)
