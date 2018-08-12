import asyncio
import functools
import typing
from datetime import datetime
from enum import Enum

import esipy
import tinydb
import discord
from discord.ext import commands

from utils.esicog import EsiCog
from utils.kvtable import KeyValueTable
from utils.log import get_logger

ZKILLBOARD_BASE_URL = "https://zkillboard.com/kill/{:d}/"
EVE_IMAGESERVER_BASE_URL = "https://imageserver.eveonline.com/Type/{:d}_64.png"
REGIONAL_INDICATOR_F = "\U0001F1EB"
ABYSSAL_SPACE_REGIONS = ("12000001", "12000002", "12000003", "12000004",
                         "12000005")


def setup(bot: commands.Bot):
    bot.add_cog(KillmailPoster(bot))


class Relevancy(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)

    @property
    def colour(self):
        return self.value["colour"]  # pylint: disable=unsubscriptable-object

    IRRELEVANT = {}
    LOSSMAIL = {"colour": discord.Colour(0x7a0000)}
    KILLMAIL = {"colour": discord.Colour(0x007a00)}


class KillmailPoster(EsiCog):
    def __init__(self, bot: commands.Bot):
        super(KillmailPoster, self).__init__(bot)

        self.logger = get_logger(__name__, bot)
        self.bot = bot
        self.config_table = KeyValueTable(self.bot.tdb, "killmails.config")
        self.channel = self.bot.get_channel(self.config_table["channel"])
        self.esi_client = esipy.EsiClient(retry_requests=True)
        self.rigs_emoji = None
        for emoji in self.channel.server.emojis:
            if str(emoji) == self.config_table["rigs_emoji"]:
                self.rigs_emoji = emoji
                break
        self.magnate_emoji = None
        for emoji in self.channel.server.emojis:
            if str(emoji) == self.config_table["magnate_emoji"]:
                self.magnate_emoji = emoji
                break
        self.relevancy_table = self.bot.tdb.table("killmails.relevancies")
        self.relevancy = tinydb.Query()

    async def on_killmail(self, package: dict, **dummy_kwargs):
        package["relevancy"] = await self.is_relevant(package)
        if package["relevancy"] is Relevancy.IRRELEVANT:
            self.logger.debug("Ignoring irrelevant killmail")
            return
        self.logger.info("Posting %s",
                         ZKILLBOARD_BASE_URL.format(package["killID"]))
        package["data"] = await self.fetch_data(package)
        embed = await self.generate_embed(package)
        message = await self.bot.send_message(self.channel, embed=embed)
        await self.add_reactions(message, package)

    async def add_reactions(self, message: discord.Message, package: dict):
        relevancy = package["relevancy"]
        if relevancy is Relevancy.LOSSMAIL:
            await self.bot.add_reaction(message, REGIONAL_INDICATOR_F)

        if self.rigs_emoji and self.should_add_rig_emoji(package):
            await self.bot.add_reaction(message, self.rigs_emoji)

        if self.magnate_emoji and self.should_add_magnate_emoji(package):
            await self.bot.add_reaction(message, self.magnate_emoji)

    def should_add_rig_emoji(self, package: dict) -> bool:
        # Flags 92, 93, 94 are rig slots
        slots = [val["flag"] for val in package["killmail"]["victim"]["items"]]
        number_of_rigs = len(list(filter(lambda x: x in (92, 93, 94), slots)))
        max_rigs = list(
            filter(
                # number of rig slots on ship
                lambda x: x["attribute_id"] == 1137,
                package["data"]["ship_type"]["dogma_attributes"]))
        if max_rigs and number_of_rigs < max_rigs[0]["value"]:
            return True

        return False

    def should_add_magnate_emoji(self, package: dict) -> bool:
        magnate_ship_id = 29248
        if package["killmail"]["victim"]["ship_type_id"] == magnate_ship_id:
            return True

        for attacker in package["killmail"]["attackers"]:
            if attacker["ship_type_id"] == magnate_ship_id:
                return True

        return False

    async def generate_embed(self, package: dict) -> discord.Embed:
        embed = discord.Embed()
        data = package["data"]
        names = {k: v["name"] for (k, v) in data.items()}

        identity = names["affiliation"]
        if "character" in names:
            identity = "{0[character]} ({0[affiliation]})".format(names)

        solar_system = names["solar_system"]
        location = "{0[solar_system]} ({0[region]})".format(names)
        if names["region"] in ABYSSAL_SPACE_REGIONS:
            solar_system = "Abyssal Space"
            location = solar_system

        embed.title = "{solar_system} | {0[ship_type]} | {identity}".format(
            names, identity=identity, solar_system=solar_system)
        embed.description = ("{identity} lost their {0[ship_type]} in "
                             "{location}\n"
                             "Total Value: {1:,} ISK\n"
                             "\u200b").format(
                                 names,
                                 package["zkb"]["totalValue"],
                                 identity=identity,
                                 location=location)
        embed.url = ZKILLBOARD_BASE_URL.format(package["killID"])
        embed.timestamp = datetime.strptime(
            package["killmail"]["killmail_time"], "%Y-%m-%dT%H:%M:%SZ")
        embed.colour = package["relevancy"].colour
        ship_type_id = package["killmail"]["victim"]["ship_type_id"]
        embed.set_thumbnail(url=EVE_IMAGESERVER_BASE_URL.format(ship_type_id))

        return embed

    async def fetch_data(self, package: dict) -> dict:
        esi_app = await self.get_esi_app()
        esi_request = functools.partial(self.esi_request, self.bot.loop,
                                        self.esi_client)
        data = {}

        operation = esi_app.op["get_universe_systems_system_id"](
            system_id=package["killmail"]["solar_system_id"])
        response = await esi_request(operation)
        data["solar_system"] = response.data

        operation = esi_app.op["get_universe_constellations_constellation_id"](
            constellation_id=response.data["constellation_id"])
        response = await esi_request(operation)
        operation = esi_app.op["get_universe_regions_region_id"](
            region_id=response.data["region_id"])
        response = await esi_request(operation)
        data["region"] = response.data

        operation = esi_app.op["get_universe_types_type_id"](
            type_id=package["killmail"]["victim"]["ship_type_id"])
        response = await esi_request(operation)
        data["ship_type"] = response.data

        if "character_id" in package["killmail"]["victim"]:
            operation = esi_app.op["get_characters_character_id"](
                character_id=package["killmail"]["victim"]["character_id"])
            response = await esi_request(operation)
            data["character"] = response.data

        if "alliance_id" in package["killmail"]["victim"]:
            operation = esi_app.op["get_alliances_alliance_id"](
                alliance_id=package["killmail"]["victim"]["alliance_id"])
            response = await esi_request(operation)
            data["affiliation"] = response.data
        else:
            operation = esi_app.op["get_corporations_corporation_id"](
                corporation_id=package["killmail"]["victim"]["corporation_id"])
            response = await esi_request(operation)
            data["affiliation"] = response.data

        return data

    async def is_relevant(self, package: dict) -> Relevancy:
        relevant_corporations = await self.get_relevant_corporations()

        victim = package["killmail"]["victim"]
        if victim["corporation_id"] in relevant_corporations:
            return Relevancy.LOSSMAIL

        for attacker in package["killmail"]["attackers"]:
            if "corporation_id" not in attacker:
                continue  # Some NPCs do not have a corporation.
            if attacker["corporation_id"] in relevant_corporations:
                return Relevancy.KILLMAIL

        return Relevancy.IRRELEVANT

    async def get_relevant_corporations(self) -> typing.Set[int]:
        corp_configs = self.relevancy_table.search(
            self.relevancy.type == "corporation")
        corp_list = set([entry["value"] for entry in corp_configs])

        alliance_configs = self.relevancy_table.search(
            self.relevancy.type == "alliance")
        alliance_list = [entry["value"] for entry in alliance_configs]

        esi_app = await self.get_esi_app()
        esi_request = functools.partial(self.esi_request, self.bot.loop,
                                        self.esi_client)
        operations = [
            esi_app.op["get_alliances_alliance_id_corporations"](
                alliance_id=alliance_id) for alliance_id in alliance_list
        ]
        responses = await asyncio.gather(*map(esi_request, operations))
        for response in responses:
            corp_list.update(response.data)

        return corp_list
