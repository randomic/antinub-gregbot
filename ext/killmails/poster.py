import typing

import tinydb
from discord.ext import commands

from utils.esicog import EsiCog
from utils.log import get_logger

ESI_SWAGGER_JSON = 'https://esi.evetech.net/latest/swagger.json'
ZKILLBOARD_BASE_URL = 'https://zkillboard.com/kill/{:d}/'


def setup(bot: commands.Bot):
    bot.add_cog(KillmailPoster(bot))


class KillmailPoster(EsiCog):
    def __init__(self, bot: commands.Bot):
        super(KillmailPoster, self).__init__(bot)

        self.logger = get_logger(__name__, bot)
        self.bot = bot
        self.relevancy_table = self.bot.tdb.table("killmails.relevancies")
        self.relevancy = tinydb.Query()

    async def on_killmail(self, package: dict):
        if not await self.is_relevant(package):
            self.logger.info("Ignoring irrelevant killmail")
            return
        self.logger.info("esi_app")
        # esi_app = await self.get_esi_app()

    async def is_relevant(self, package: dict) -> bool:
        victim = package["killmail"]["victim"]
        if await self.is_corporation_relevant(victim["corporation_id"]):
            return True

        for attacker in package["killmail"]["attackers"]:
            if "corporation_id" not in attacker:
                continue  # Some NPCs do not have a corporation.
            if await self.is_corporation_relevant("corporation_id"):
                return True

        return False

    async def is_corporation_relevant(self, corporation_id: int) -> bool:
        if corporation_id in await self.get_relevant_corporations():
            return True

        if corporation_id in await self.get_relevant_alliances():
            return True

        return False

    async def get_relevant_corporations(self) -> typing.List[int]:
        corps = self.relevancy_table.search(
            self.relevancy.type == "corporation")
        return [entry["value"] for entry in corps]

    async def get_relevant_alliances(self) -> typing.List[int]:
        return []
