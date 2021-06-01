import itertools

from discordself import Client, Status

from utils.colourthief import get_embed_colour
from utils.log import get_logger
from utils.messaging import notify_owner
from discordself.ext import commands


class DiscordRelay(commands.Cog, name='DiscordRelay'):
    def __init__(self, bot, config):
        self.logger = get_logger(__name__)
        self.bot = bot
        self.config = config
        self.client = Client(loop=bot.loop)
        self.client.event(self.on_ready)
        self.client.event(self.on_message)
        self._embed_colour_cache = {}
        bot.loop.create_task(self.client.start(config["token"]))

    def disconnect(self):
        self.bot.loop.create_task(self.client.logout())

    def get_health(self):
        state = {}
        state['ready'] = self.client.is_ready
        state['description'] = self.config['description']
        if self.client.is_ready:
            state['guilds'] = self.client.guilds

        return state

    def get_message_logo(self, message):
        '''
        Extracts message logo url from the guild logo. Falls back to the default logo otherwise.
        '''
        if message.guild is not None:
            icon_asset = message.guild.icon_url
            self.logger.debug('Guild {} asset {} is_animated {}'.format(message.guild.id, str(icon_asset), message.guild.is_icon_animated()))
            if icon_asset is not None:
                return str(icon_asset)

        return self.config['default_icon_url']

    def get_cached_embed_colour(self, url):
        '''
        Stores colourthief output locally for reuse
        '''
        if url in self._embed_colour_cache:
            return self._embed_colour_cache[url]

        colour = get_embed_colour(url)
        self._embed_colour_cache[url] = colour
        return colour

    def route_message(self, message):
        '''
        Decides which messages go where based on the .yaml route config provided at startup
        '''
        guild = message.guild.id
        channel = message.channel.id
        destinations = []
        # Attempt to apply routing rules based on guild and channel ids
        for route in self.config['routes']:
            if 'from_guilds' in route and guild in route['from_guilds'] or\
            'from_channels' in route and channel in route['from_channels']:
                # Make sure the source channel is not in the ignore_channels list
                if not ('ignore_channels' in route and channel in route['ignore_channels']):
                    destinations.extend(route['destinations'])

        # If no destinations were found, route to catch-all destinations
        if len(destinations) == 0:
            default_routes = filter(\
                lambda route: 'from_guilds' not in route and 'from_channels' not in route, \
                self.config['routes'])
            default_destinations = map(lambda x: x['destinations'], default_routes)
            destinations = list(itertools.chain.from_iterable(default_destinations))

        self.logger.debug('Routed message from guild {} ({}) channel {} ({}) to destinations {}'\
            .format(message.guild.name, message.guild.id, message.channel.name, message.channel.id,\
                ','.join(map(lambda x: str(x['channel_id']), destinations)) if len(destinations) > 0 else 'None'))
        return destinations

    async def on_ready(self):
        await self.client.change_presence(status=Status.invisible)

    async def on_message(self, message):
        if message.mention_everyone:
            message_logo = self.get_message_logo(message)
            package = {
                'body': message.clean_content,
                'sender': message.author.display_name,
                'destinations': self.route_message(message),
                'description': '{}: {}'.format(
                    message.guild.name,
                    message.channel.name or "Private Channel"
                ),
                'logo_url': message_logo,
                'embed_colour': self.get_cached_embed_colour(message_logo)
            }
            self.bot.dispatch('broadcast', package)
