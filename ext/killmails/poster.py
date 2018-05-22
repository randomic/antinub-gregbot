import typing
from datetime import datetime

import tinydb
import discord
from discord.ext import commands

from utils.esicog import EsiCog
from utils.kvtable import KeyValueTable
from utils.log import get_logger

ESI_SWAGGER_JSON = 'https://esi.evetech.net/latest/swagger.json'
ZKILLBOARD_BASE_URL = 'https://zkillboard.com/kill/{:d}/'
EVE_IMAGESERVER_BASE_URL = "https://imageserver.eveonline.com/Type/{:d}_64.png"


def setup(bot: commands.Bot):
    bot.add_cog(KillmailPoster(bot))


class KillmailPoster(EsiCog):
    def __init__(self, bot: commands.Bot):
        super(KillmailPoster, self).__init__(bot)

        self.logger = get_logger(__name__, bot)
        self.bot = bot
        self.config_table = KeyValueTable(self.bot.tdb, "killmails.config")
        self.relevancy_table = self.bot.tdb.table("killmails.relevancies")
        self.relevancy = tinydb.Query()

    async def on_killmail(self, package: dict, **dummy_kwargs):
        if not await self.is_relevant(package):
            self.logger.debug("Ignoring irrelevant killmail")
            return
        embed = await self.generate_embed(package)
        message = await self.bot.send_message(
            self.bot.get_channel(self.config_table["channel"]), embed=embed)
        await self.add_reactions(message)

    async def add_reactions(self, message: discord.Message):
        # Flags 92, 93, 94 are rig slots
        pass

    async def generate_embed(self, package: dict) -> discord.Embed:
        embed = discord.Embed()

        names = await self.fetch_names(package)
        embed.title = "{} | {} | {}".format(
            names["solar_system"], names["ship_type"], names["character"])
        embed.description = ("{} lost their {} in {} ({})\n"
                             "Total Value: {:,} ISK\n"
                             "\u200b").format(
                                 names["character"], names["ship_type"],
                                 names["solar_system"], names["region"],
                                 package["zkb"]["totalValue"])
        embed.url = ZKILLBOARD_BASE_URL.format(package["killID"])
        embed.timestamp = datetime.strptime(
            package["killmail"]["killmail_time"], "%Y-%m-%dT%H:%M:%SZ")
        embed.colour = package["colour"]
        ship_type_id = package["killmail"]["victim"]["ship_type_id"]
        embed.set_thumbnail(url=EVE_IMAGESERVER_BASE_URL.format(ship_type_id))

        return embed

    async def fetch_names(self, package: dict) -> dict:
        names = {}
        esi_app = await self.get_esi_app()
        esi_client = await self.get_esi_client()

        operation = esi_app.op["get_universe_systems_system_id"](
            system_id=package["killmail"]["solar_system_id"])
        response = await self.esi_request(self.bot.loop, esi_client, operation)
        names["solar_system"] = response.data["name"]

        operation = esi_app.op["get_universe_constellations_constellation_id"](
            constellation_id=response.data["constellation_id"])
        response = await self.esi_request(self.bot.loop, esi_client, operation)
        operation = esi_app.op["get_universe_regions_region_id"](
            region_id=response.data["region_id"])
        response = await self.esi_request(self.bot.loop, esi_client, operation)
        names["region"] = response.data["name"]

        operation = esi_app.op["get_universe_types_type_id"](
            type_id=package["killmail"]["victim"]["ship_type_id"])
        response = await self.esi_request(self.bot.loop, esi_client, operation)
        names["ship_type"] = response.data["name"]

        operation = esi_app.op["get_characters_character_id"](
            character_id=package["killmail"]["victim"]["character_id"])
        response = await self.esi_request(self.bot.loop, esi_client, operation)
        names["character"] = response.data["name"]

        return names

    async def is_relevant(self, package: dict) -> bool:
        victim = package["killmail"]["victim"]
        if await self.is_corporation_relevant(victim["corporation_id"]):
            #  Mark killmail as a loss
            package["colour"] = discord.Colour.dark_red()
            return True

        for attacker in package["killmail"]["attackers"]:
            if "corporation_id" not in attacker:
                continue  # Some NPCs do not have a corporation.
            if await self.is_corporation_relevant("corporation_id"):
                #  Mark killmail as a kill
                package["colour"] = discord.Colour.dark_green()
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
        corp_ids = set()
        alliances = self.relevancy_table.search(
            self.relevancy.type == "alliance")
        alliance_ids = [entry["value"] for entry in alliances]

        for alliance_id in alliance_ids:
            alliance_corp_ids = await self.get_alliance_corporations(
                alliance_id)
            corp_ids.update(alliance_corp_ids)

        return list(corp_ids)

    async def get_alliance_corporations(self,
                                        alliance_id: int) -> typing.List[int]:
        esi_app = await self.get_esi_app()
        operation = esi_app.op["get_alliances_alliance_id_corporations"](
            alliance_id=alliance_id)

        esi_client = await self.get_esi_client()
        response = await self.esi_request(self.bot.loop, esi_client, operation)
        return response.data
