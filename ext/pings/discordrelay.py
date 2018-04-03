from discord import Client, Status

from utils.colourthief import get_embed_colour
from utils.messaging import notify_owner


class DiscordRelay:
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.config["embed_colour"] = get_embed_colour(self.config["logo_url"])
        self.client = Client(loop=bot.loop)
        self.client.event(self.on_ready)
        self.client.event(self.on_message)
        bot.loop.create_task(self.client.start(config["token"], bot=False))

    def disconnect(self):
        self.bot.loop.create_task(self.client.logout())

    def get_health(self):
        if self.client.is_logged_in:
            resp = '\n  \u2714 {} - Connected'
        else:
            resp = '\n  \u2716 {} - Disconnected'
        fmt = ", ".join(map(lambda x: x.name, self.client.servers))
        return resp.format(fmt)

    async def on_ready(self):
        await self.client.change_presence(status=Status.invisible)

    async def on_message(self, message):
        if message.mention_everyone:
            package = {
                'body': message.clean_content,
                'sender': message.channel.name or "Private Channel",
                'destinations': self.config['destinations'],
                'description': self.config['description'],
                'logo_url': self.config['logo_url'],
                'embed_colour': self.config["embed_colour"]
            }
            self.bot.dispatch('broadcast', package)
