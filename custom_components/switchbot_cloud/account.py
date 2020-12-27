"""Account Class."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .api import SwitchBotCloudApiClient
from .const import (
    DOMAIN,
    LOGGER,
    NEW_COVER,
    NEW_SENSOR,
    NEW_SWITCH,
    SUPPORTED_PLATFORMS,
)


DEVICE_TYPE_MAPPING = {
    "Curtain": [NEW_COVER, NEW_SENSOR],
    "CurtainGroup": [NEW_COVER, NEW_SENSOR],
    "Bot": [NEW_SWITCH],
}


@callback
def get_account_from_config_entry(hass, config_entry):
    """Return account with an id."""
    return hass.data[DOMAIN][config_entry.entry_id]


class SwitchBotCloudAccount:
    """Account Class."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the account."""
        self.hass = hass
        self.config_entry = config_entry

        self.client = None
        self.known_ids = {}
        self.listeners = []

        for type in [NEW_COVER, NEW_SENSOR, NEW_SWITCH]:
            self.known_ids[type] = []

    @property
    def id(self) -> str:
        """Return ID."""
        return self.config_entry.entry_id

    @property
    def username(self) -> str:
        """Return the username of the account."""
        return self.config_entry.data[CONF_USERNAME]

    @callback
    def async_signal_new_device(self, device_type: str) -> str:
        """Return event to signal new device."""
        new_device = {
            NEW_COVER: f"switchbot_cloud_new_cover_{self.id}",
            NEW_SENSOR: f"switchbot_cloud_new_sensor_{self.id}",
            NEW_SWITCH: f"switchbot_cloud_new_switch_{self.id}",
        }

        return new_device[device_type]

    async def async_setup(self) -> bool:
        """Set up an account."""
        username = self.config_entry.data.get(CONF_USERNAME)
        password = self.config_entry.data.get(CONF_PASSWORD)

        session = async_get_clientsession(self.hass)
        self.client = SwitchBotCloudApiClient(session)
        await self.client.authenticate(username, password)

        for component in SUPPORTED_PLATFORMS:
            self.hass.async_create_task(
                self.hass.config_entries.async_forward_entry_setup(
                    self.config_entry, component
                )
            )

        self.client.start(self.async_update_devices_callback)

        return True

    @callback
    def async_update_devices_callback(self, devices: list) -> None:
        """Handle update of device list."""
        new_devices = {}

        for device in devices:
            device_id = device.id
            device_type = device.type

            if device_type not in DEVICE_TYPE_MAPPING:
                continue

            for type in DEVICE_TYPE_MAPPING[device_type]:
                if device_id in self.known_ids[type]:
                    continue

                LOGGER.debug(
                    "Found %s device to add %s: %s", device_type, type, device_id
                )

                if type not in new_devices:
                    new_devices[type] = []

                new_devices[type].append(device)

        for device_type, devices in new_devices.items():
            async_dispatcher_send(
                self.hass, self.async_signal_new_device(device_type), devices
            )

    @callback
    def shutdown(self, event) -> None:
        """Shutdown."""
        self.client.stop()

    async def async_reset(self) -> bool:
        """Reset this account to default state."""
        self.client.stop()
        self.client = None

        for component in SUPPORTED_PLATFORMS:
            await self.hass.config_entries.async_forward_entry_unload(
                self.config_entry, component
            )

        for unsub_dispatcher in self.listeners:
            unsub_dispatcher()

        self.listeners = []
        self.known_ids = {}

        for type in [NEW_COVER, NEW_SENSOR, NEW_SWITCH]:
            self.known_ids[type] = []

        return True
