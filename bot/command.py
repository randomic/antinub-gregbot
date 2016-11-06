import logging
import config

class Main:
    '''Creates a listener for the specified discord client
    which will listen for keyphrases and execute code on
    receiving them'''
    def __init__(self, discordClient):
        self.client = discordClient
        self.logger = logging.getLogger(__name__)
        self.owner = config.OWNER_ID
        
        @self.client.async_event
        def on_message(message):
            if message.content.startswith('!'):
                command = message.content[1:].split()
                if command[0] == 'stop':
                    if self.isOwner(message.author):
                        self.logger.info('Received stop command from owner')
                        yield from self.client.send_message(message.channel, 'cyka blyat bye')
                        yield from self.client.logout()
                    else:
                        self.logger.warn('Non-owner attempted to use stop command')
                        yield from self.client.send_message(message.channel, 'idi nahui')

    def isOwner(self, user):
        'Check whether or not the user is the owner of the bot'
        return user.id == self.owner          