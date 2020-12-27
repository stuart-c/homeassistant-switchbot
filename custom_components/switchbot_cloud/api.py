"""Sample API Client."""
import aiohttp
import asyncio

from switchbot import SwitchBot

from .const import LOGGER


class SwitchBotCloudApiClient:
    """Class to integration with SwitchBot Python library."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Sample API Client."""
        self._loop = asyncio.get_event_loop()
        self._switchbot = None
        self._task = None

    async def authenticate(self, username: str, password: str) -> None:
        """Authenticate."""
        assert self._switchbot is None

        self._switchbot = await self._loop.run_in_executor(None, SwitchBot, username)
        await self._loop.run_in_executor(None, self._switchbot.authenticate, password)

    def start(self, callback):
        """Start coroutine to check devices."""
        assert self._switchbot is not None

        if self._task:
            return

        async def list_devices():
            """Coroutine to periodically get devices."""
            while True:
                devices = await self._loop.run_in_executor(
                    None, getattr, self._switchbot, "devices"
                )

                if devices:
                    callback(devices)

                await asyncio.sleep(60)

        self._task = self._loop.create_task(list_devices())

    def stop(self):
        """End coroutine."""
        if not self._task:
            return

        self._task.cancel()
        self._task = None
