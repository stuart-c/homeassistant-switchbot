"""Cover platform for switchbot_cloud."""
from datetime import timedelta
from homeassistant.components.cover import (
    CoverEntity,
    DEVICE_CLASS_CURTAIN,
    ENTITY_ID_FORMAT,
    SUPPORT_CLOSE,
    SUPPORT_OPEN,
    SUPPORT_SET_POSITION,
)
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import async_generate_entity_id

from .account import get_account_from_config_entry
from .const import DOMAIN, LOGGER, NAME, NEW_COVER, VERSION

SCAN_INTERVAL = timedelta(seconds=30)
PARALLEL_UPDATES = 1


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up a covers for SwitchBot Cloud."""
    account = get_account_from_config_entry(hass, config_entry)

    LOGGER.debug("Setup covers for %s", account.username)

    @callback
    def async_add_cover(devices):
        entities = []

        for device in devices:
            device_id = device.id
            name = device.name
            position = device.position

            if device_id in account.known_ids[NEW_COVER]:
                continue

            entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, name, hass=hass)

            LOGGER.debug("Initialize %s", entity_id)

            entities.append(
                SwitchBotCloudCover(entity_id, device_id, device, name, position)
            )

            account.known_ids[NEW_COVER].append(device_id)

        if entities:
            async_add_entities(entities)

    account.listeners.append(
        async_dispatcher_connect(
            hass, account.async_signal_new_device(NEW_COVER), async_add_cover
        )
    )


class SwitchBotCloudCover(CoverEntity):
    """switchbot_cloud Cover class."""

    def __init__(self, entity_id, device_id, device, name, position):
        """Initialize a sensor."""
        super().__init__()

        self.entity_id = entity_id
        self._device = device

        self._unique_id = device_id
        self._name = name
        self._position = position

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def device_info(self):
        """Device info."""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": NAME,
            "model": VERSION,
        }

    @property
    def current_cover_position(self):
        """Return current position of cover.

        None is unknown, 0 is closed, 100 is fully open.
        """
        return 100 - self._position

    @property
    def is_closed(self):
        """Return if the cover is closed or not."""
        return self._position == 100

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_class(self):
        """Return the class of the sensor."""
        return DEVICE_CLASS_CURTAIN

    @property
    def supported_features(self):
        """Flag supported features."""
        supported_features = SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_SET_POSITION

        return supported_features

    async def async_update(self):
        """Update the sensor state."""
        self._name = await self.hass.async_add_executor_job(
            getattr, self._device, "name"
        )
        position = await self.hass.async_add_executor_job(
            getattr, self._device, "position"
        )

        if position >= 95:
            position = 100
        if position <= 5:
            position = 0

        self._position = position

        LOGGER.debug("Update cover state: %s = %s", self.entity_id, self._position)

    async def async_open_cover(self):
        """Open the cover."""
        await self.hass.async_add_executor_job(self._device.open)
        self._position = 0
        self.async_schedule_update_ha_state()

    async def async_close_cover(self):
        """Close cover."""
        await self.hass.async_add_executor_job(self._device.close)
        self._position = 100
        self.async_schedule_update_ha_state()

    async def async_set_cover_position(self, position):
        """Move the cover to a specific position."""
        await self.hass.async_add_executor_job(self._device.move, 100 - position)
        self._position = 100 - position
        self.async_schedule_update_ha_state()
