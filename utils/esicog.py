import esipy
from discord.ext import commands
import time

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
        self._esi_app_task = bot.loop.run_in_executor(None, get_esi_app)
        self._esi_client_task = bot.loop.run_in_executor(None, get_esi_client)

    async def get_esi_app(self, bot: commands.Bot):
        return await self._esi_app_task

    async def get_esi_client(self, bot: commands.Bot):
        return await self._esi_client_task
