import logging
from datetime import datetime

from discord.embeds import Embed
from discord.ext import commands
from utils.log import get_logger
from utils.messaging import Paginate, notify_owner
from utils.checks import is_owner_private_channel

from .discordrelay import DiscordRelay
from .jabberrelay import JabberRelay


def setup(bot: commands.Bot):
    bot.add_cog(PingAggregator(bot))


class PingAggregator(commands.Cog, name='PingAggregator'):
    '''A cog which connects to config defined xmpp servers and relays messages
    from certain senders to the config defined channel'''

    def __init__(self, bot):
        self.logger = get_logger(__name__)
        self.bot = bot
        bot.add_listener(self.on_broadcast)
        self.relays = []
        self.create_clients(bot.ext_config['pings'])

    def create_clients(self, config):
        'Creates an JabberRelay client for each server specified'
        for jabber_config in config.get("jabber_relays", []):
            self.relays.append(
                JabberRelay(self.bot, jabber_config, self.logger))
        for discord_config in config.get("discord_relays", []):
            self.relays.append(DiscordRelay(self.bot, discord_config))

    async def on_broadcast(self, package):
        'Relay message to discord, ignore if it is a duplicate'
        body = package['body']

        self.logger.info('Relaying message from %s', package['sender'])

        embeds = []
        paginate = Paginate(body, enclose=('', ''), page_size=1900)
        for page in paginate:
            embed = self.ping_embed(package, page, paginate)
            embeds.append(embed)

        for destination in package['destinations']:
            channel_id = destination['channel_id']
            channel = self.bot.get_channel(channel_id)

            if channel:
                embed = embeds[0]
                await channel.send(embed=embed, content=destination.get('prefix')
                )  # Only show prefix on first page.
                for embed in embeds[1:]:
                    await channel.send(embed=embed)
            else:
                await notify_owner(self.bot,
                                   ['Invalid channel: {}'.format(channel_id)])


    @commands.command()
    @commands.check(is_owner_private_channel)
    async def relay_health(self, ctx):
        'Command describing status of relays'
        if self.relays:
            response = ''
            for relay in self.relays:
                state = relay.get_health()
                if state['ready']:
                    guild_str = ", ".join(map(lambda x: x.name, state['guilds']))
                    response += '{}: ({}) - :white_check_mark:\n'\
                        .format(state['description'], guild_str)
                else:
                    response += '{}- :negative_squared_cross_mark:\n'

        else:
            response = 'No relays initialised.'
        return await ctx.send(response)

    @staticmethod
    def ping_embed(package, message, paginate):
        'Formats and generates the embed for the ping'
        embed = Embed()
        currentmsg = paginate.pages_yielded
        totalmsgs = currentmsg + paginate.pages_left

        if currentmsg == 1:
            embed.title = package['sender']
            embed.set_author(name=package['description'])

        embed.description = message
        embed.set_thumbnail(url=package['logo_url'])
        if totalmsgs > 1:
            embed.set_footer(
                text='Message {}/{}'.format(currentmsg, totalmsgs))
        embed.timestamp = datetime.utcnow()
        embed.colour = package['embed_colour']

        return embed

    def __unload(self):
        for relay in self.relays:
            relay.disconnect()
