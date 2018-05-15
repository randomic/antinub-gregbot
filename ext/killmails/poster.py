from discord.ext import commands

from utils.esicog import EsiCog
from utils.log import get_logger

ESI_SWAGGER_JSON = 'https://esi.evetech.net/latest/swagger.json'


def setup(bot: commands.Bot):
    bot.add_cog(KillmailPoster(bot))


class KillmailPoster(EsiCog):
    def __init__(self, bot: commands.Bot):
        super(KillmailPoster, self).__init__(bot)

        self.logger = get_logger(__name__, bot)
        self.bot = bot
        self.relevancy_table = self.bot.tdb.table("killmails.relevancies")

    async def on_killmail(self, killmail: dict):
        if not await self.is_relevant(killmail):
            return
        self.logger.info("esi_app")

    async def is_relevant(self, killmail: dict) -> bool:
        esi_app = await self.get_esi_app()
        return True
