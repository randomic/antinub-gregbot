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
from aioxmpp.structs import LanguageRange

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
            self.xmpp_relays.append(XmppRelay(self.bot, server, self.logger))

    def get_health(self):
        'Returns a string describing the status of this cog'
        if self.xmpp_relays:
            response = ''
            for xmpp_relay in self.xmpp_relays:
                if xmpp_relay.established:
                    resp = '\n  \u2714 {} - Connected'
                else:
                    resp = '\n  \u2716 {} - Disconnected'
                response += resp.format(xmpp_relay.local_jid.domain)
        else:
            response = '\n  \u2716 No relays initialised'
        return response

    async def on_broadcast(self, package):
        'Relay message to discord, ignore if it is a duplicate'
        body = package['body']

        idx = body.rfind('Broadcast sent at ')
        raw_msg = body[:idx] if idx > 0 else body

        if raw_msg != self.last_msg:
            self.last_msg = raw_msg
            self.logger.info('Relaying message from %s',
                             package['sender'])
            r_message = paginate(package['body'], aff='', pref='',
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
                             package['sender'])

    def ping_embed(self, package, message, r_message):
        'Formats and generates the embed for the ping'
        embed = Embed()
        totalmsgs = len(r_message)
        currentmsg = r_message.index(message)

        if not currentmsg:
            embed.title = package['sender']
            embed.set_author(name=package['description'])

        embed.description = message
        embed.set_thumbnail(url=package['logo_url'])
        embed.set_footer(text='Message {}/{}'.format(currentmsg+1, totalmsgs))
        embed.timestamp = datetime.now()

        return embed

    def __unload(self):
        for xmpp_relay in self.xmpp_relays:
            xmpp_relay.presence = aioxmpp.PresenceState(False)


class XmppRelay(aioxmpp.PresenceManagedClient):
    '''Connects to an XMPP server and relays broadcasts
    to a specified discord channel'''
    def __init__(self, bot, jabber_server, logger):
        super(XmppRelay, self).__init__(
            aioxmpp.JID.fromstr(jabber_server['jabber_id']),
            aioxmpp.make_security_layer(jabber_server['password'], no_verify=True),
            logger=logger
        )

        self.bot = bot
        self.relay_from = jabber_server['relay_from']
        self.jabber_server = jabber_server
        self.languages = [LanguageRange(tag='en'), LanguageRange.WILDCARD]
        self.summon(aioxmpp.DiscoServer)
        self.summon(aioxmpp.RosterClient)

        message_dispatcher = self.summon(
            aioxmpp.dispatcher.SimpleMessageDispatcher
        )
        message_dispatcher.register_callback(
            None,
            None,
            self.message_receieved
        )

        self.presence = aioxmpp.PresenceState(True, aioxmpp.PresenceShow.AWAY)

    def message_receieved(self, message):
        'Pass messages from specified senders to the cog for relaying'
        sender = str(message.from_.bare())
        self.logger.debug('Recieved message from %s', sender)
        if not message.body:
            return self.logger.info('Ignored empty message from %s', sender)
        if sender not in self.relay_from:
            return self.logger.info('Ignored message from %s', sender)
        package = {
            'body': message.body.lookup(self.languages),
            'sender': sender,
            'forward_to': self.jabber_server['forward_to'],
            'description': self.jabber_server['description'],
            'prefix': self.jabber_server['prefix'],
            'logo_url': self.jabber_server['logo_url']
        }
        self.bot.dispatch('broadcast', package)
