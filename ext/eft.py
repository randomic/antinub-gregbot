'''
Cog that copies EFT-formatted fits into an embed.
'''

import logging
import urllib.request, json, re

from datetime import datetime

import discord.ext.commands as commands
import utils.checks as checks
from discord.embeds import Embed

def setup(bot):
    'Adds the cog to the provided Discord bot'
    bot.add_cog(EFT(bot))
    
class EFT:
    'A cog that copies EFT-formatted fits to an embed'
    def __init__(self, bot):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
    
    
    # @commands.command(pass_context=True)
    # async def eft(self, context):
        # content = context.message.content
        # content_list = content.split(']',1)
        
        # content_list[0] = content_list[0].split(' ', 1)[1]
        
        
        # embed = self.eftembed(content_list[0] + ']', content_list[1])
        # await self.bot.send_message(context.message.channel, embed = embed)
        # await self.bot.delete_message(context.message)
        
        
    async def on_message(self, message):
        content = str(message.content)
        p = re.compile('\[(.*?)\]\n(.*)', re.DOTALL)
        m = p.match(content)
        if(m != None):
            embed = self.eftembed(m.group(1),m.group(2))
            await self.bot.send_message(message.channel, embed = embed)
            await self.bot.delete_message(message)
            
    def eftembed(self, title, fit):
        embed = Embed()
        
        p = re.compile('(.*),.*')
        m = p.match(title)
        type = m.group(1)
        type = type.replace(" ", "%20")
        
        file_url = 'https://www.fuzzwork.co.uk/api/typeid.php?typename=' + type
        
        with urllib.request.urlopen(file_url) as url:
            data = json.load(url)
            typeid = data["typeID"]
        
        image_url = 'https://imageserver.eveonline.com/Render/' + str(typeid) + '_128.png'
        
        embed.set_thumbnail(url = image_url)
        embed.title = title
        embed.description = fit
        embed.set_footer(text = 'Reformatted by spaibot, original deleted.')
        embed.timestamp = datetime.now()
        
        return embed