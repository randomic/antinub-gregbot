import logging

import esipy
from discord.ext import commands

from utils.log import get_logger

ESI_SWAGGER_JSON = 'https://esi.evetech.net/latest/swagger.json'
ESI_APP: esipy.App = None
ESI_CLIENT: esipy.EsiClient = None


def get_esi_app():
    global ESI_APP

    if not ESI_APP:
        ESI_APP = esipy.App.create(url=ESI_SWAGGER_JSON)
    return ESI_APP


def get_esi_client():
    global ESI_CLIENT

    if not ESI_CLIENT:
        ESI_CLIENT = esipy.EsiClient()
    return ESI_CLIENT


class EsiCog:
    def __init__(self, bot: commands.Bot):
        logger = get_logger(__name__, bot)

        logger.info("Creating esipy App...")
        self._esi_app_task = bot.loop.run_in_executor(None, get_esi_app)
        self._esi_app_task.add_done_callback(
            lambda f: logger.info("esipy App created"))

        logger.info("Creating esipy EsiClient...")
        self._esi_client_task = bot.loop.run_in_executor(None, get_esi_client)
        self._esi_client_task.add_done_callback(
            lambda f: logger.info("esipy EsiClient created"))

    async def get_esi_app(self):
        return await self._esi_app_task

    async def get_esi_client(self):
        return await self._esi_client_task
