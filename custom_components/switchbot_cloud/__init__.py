"""
Custom integration to integrate switchbot_cloud with Home Assistant.

For more details about this integration, please refer to
https://github.com/stuart-c/homeassistant-switchbot
"""
import asyncio

from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import Config, HomeAssistant

from .account import SwitchBotCloudAccount
from .const import DOMAIN, LOGGER, STARTUP_MESSAGE

SCAN_INTERVAL = timedelta(minutes=5)


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        LOGGER.info(STARTUP_MESSAGE)

    account = SwitchBotCloudAccount(hass, config_entry)

    if not await account.async_setup():
        return False

    hass.data[DOMAIN][config_entry.entry_id] = account

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, account.shutdown)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload config entry."""
    account = hass.data[DOMAIN].pop(config_entry.unique_id)

    return await account.async_reset()
