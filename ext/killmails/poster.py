import logging

import esipy
from discord.ext import commands


ESI_SWAGGER_JSON = 'https://esi.evetech.net/latest/swagger.json'


def setup(bot: commands.Bot):
    bot.add_cog(KillmailPoster(bot))


class KillmailPoster:
    def __init__(self, bot: commands.Bot):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.relevancy_table = self.bot.tdb.table("killmails.relevancies")

        self.esi_app = esipy.App.create(url=ESI_SWAGGER_JSON)
        self.esi_client = esipy.EsiClient()

    async def on_killmail(self, killmail: dict):
        if not self.is_relevant(killmail):
            return


    def is_relevant(self, killmail: dict) -> bool:
        return True

