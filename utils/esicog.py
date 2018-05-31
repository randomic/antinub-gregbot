import asyncio

import esipy
from discord.ext import commands
from requests.adapters import DEFAULT_POOLSIZE

from utils.log import get_logger

ESI_SWAGGER_JSON = 'https://esi.evetech.net/dev/swagger.json'


class EsiCog:
    _esi_app_task: asyncio.Task = None
    _semaphore = asyncio.Semaphore(DEFAULT_POOLSIZE)

    def __init__(self, bot: commands.Bot):
        logger = get_logger(__name__, bot)

        if self._esi_app_task is None:
            logger.info("Creating esipy App...")
            self._esi_app_task = bot.loop.run_in_executor(
                None, self._create_esi_app)
            self._esi_app_task.add_done_callback(
                lambda f: logger.info("esipy App created"))

    def __unload(self):
        self._esi_app_task.cancel()

    async def get_esi_app(self) -> asyncio.Task:
        return await self._esi_app_task

    def _create_esi_app(self):
        return esipy.App.create(url=ESI_SWAGGER_JSON)

    async def esi_request(self, loop, client, operation):
        async with self._semaphore:
            return await loop.run_in_executor(None, client.request, operation)
