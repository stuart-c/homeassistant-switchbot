"""Sample API Client."""
import logging
import asyncio
import aiohttp


_LOGGER: logging.Logger = logging.getLogger(__package__)


class SwitchBotCloudApiClient:
    def __init__(
        self, username: str, password: str, session: aiohttp.ClientSession
    ) -> None:
        """Sample API Client."""
        self._loop = asyncio.get_event_loop()
        self._switchbot = SwitchBot(username)

        result = await self._loop.run_in_executor(
            None, self._switchbot.authenticate, password
        )
