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
        self.config["embed_colour"] = get_embed_colour(self.config["logo_url"])
        self.client = Client(loop=bot.loop)
        self.client.event(self.on_ready)
        self.client.event(self.on_message)
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

    def route_message(self, message):
        guild = message.guild.id
        channel = message.channel.id
        destinations = []
        for route in self.config['routes']:
            if 'from_guilds' in route and guild in route['from_guilds'] or\
            'from_channels' in route and channel in route['from_channels']:
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
            package = {
                'body': message.clean_content,
                'sender': message.author.display_name,
                'destinations': self.route_message(message),
                'description': '{}: {}'.format(
                    message.guild.name,
                    message.channel.name or "Private Channel"
                ),
                'logo_url': self.config['logo_url'],
                'embed_colour': self.config["embed_colour"]
            }
            self.bot.dispatch('broadcast', package)
