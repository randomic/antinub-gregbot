from discordself import Client, Status

from utils.colourthief import get_embed_colour
from utils.messaging import notify_owner
from discordself.ext import commands


class DiscordRelay(commands.Cog, name='DiscordRelay'):
    def __init__(self, bot, config):
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

    async def on_ready(self):
        await self.client.change_presence(status=Status.invisible)

    async def on_message(self, message):
        if message.mention_everyone:
            package = {
                'body': message.clean_content,
                'sender': message.author.display_name,
                'destinations': self.config['destinations'],
                'description': '{}: {}'.format(
                    message.guild.name,
                    message.channel.name or "Private Channel"
                ),
                'logo_url': self.config['logo_url'],
                'embed_colour': self.config["embed_colour"]
            }
            self.bot.dispatch('broadcast', package)
