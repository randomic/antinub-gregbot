'''
Jabber relay cog made for antinub-gregbot project.

When added to a bot it creates an xmpp client per one configured in
config.JABBER_SERVERS
It will then listen on those servers and relay any messages received if
they are sent by a jid in the config.JABBER_SERVERS['relay_from'] list
'''
import aioxmpp
from aioxmpp.structs import LanguageRange

from utils.colourthief import get_embed_colour


class JabberRelay(aioxmpp.PresenceManagedClient):
    '''Connects to an XMPP server and relays broadcasts
    to a specified discord channel'''
    def __init__(self, bot, jabber_server, logger):
        config = jabber_server['jabber_id'].split(':')
        jabber_id = aioxmpp.JID.fromstr(config[0])
        override_peer = []
        if len(config) > 1:
            port = config[1]
            override_peer = [(
                jabber_id.domain,
                port,
                aioxmpp.connector.STARTTLSConnector()
            )]

        super(JabberRelay, self).__init__(
            aioxmpp.JID.fromstr(jabber_server['jabber_id']),
            aioxmpp.make_security_layer(jabber_server['password'], no_verify=True),
            override_peer=override_peer,
            logger=logger
        )

        self.bot = bot
        self.relay_from = jabber_server['relay_from']
        self.jabber_server = jabber_server
        self.embed_colour = get_embed_colour(jabber_server['logo_url'])
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

    def disconnect(self):
        self.presence = aioxmpp.PresenceState(False)

    def get_health(self):
        if self.established:
            resp = '\n  \u2714 {} - Connected'
        else:
            resp = '\n  \u2716 {} - Disconnected'
        return resp.format(self.local_jid.domain)

    def message_receieved(self, message):
        'Pass messages from specified senders to the cog for relaying'
        sender = str(message.from_.bare())
        self.logger.debug('Recieved message from %s', sender)
        if not message.body:
            return self.logger.debug('Ignored empty message from %s', sender)
        if sender not in self.relay_from:
            return self.logger.info('Ignored message from %s', sender)
        package = {
            'body': message.body.lookup(self.languages),
            'sender': sender,
            'destinations': self.jabber_server['destinations'],
            'description': self.jabber_server['description'],
            'logo_url': self.jabber_server['logo_url'],
            'embed_colour': self.embed_colour
        }
        self.bot.dispatch('broadcast', package)
