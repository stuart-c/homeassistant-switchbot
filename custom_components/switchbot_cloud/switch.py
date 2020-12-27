"""Switch platform for switchbot_cloud."""
from datetime import timedelta
from homeassistant.components.switch import ENTITY_ID_FORMAT, SwitchEntity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import async_generate_entity_id

from .account import get_account_from_config_entry
from .const import DOMAIN, LOGGER, NAME, NEW_SWITCH, VERSION

SCAN_INTERVAL = timedelta(seconds=30)
PARALLEL_UPDATES = 1


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up a covers for SwitchBot Cloud."""
    account = get_account_from_config_entry(hass, config_entry)

    LOGGER.debug("Setup switches for %s", account.username)

    @callback
    def async_add_switch(devices):
        entities = []

        for device in devices:
            device_id = device.id
            name = device.name
            state = device.state

            if device_id in account.known_ids[NEW_SWITCH]:
                continue

            entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, name, hass=hass)

            LOGGER.debug("Initialize %s", entity_id)

            entities.append(
                SwitchBotCloudBinarySwitch(entity_id, device_id, device, name, state)
            )

            account.known_ids[NEW_SWITCH].append(device_id)

        if entities:
            async_add_entities(entities)

    account.listeners.append(
        async_dispatcher_connect(
            hass, account.async_signal_new_device(NEW_SWITCH), async_add_switch
        )
    )


class SwitchBotCloudBinarySwitch(SwitchEntity):
    """switchbot_cloud Switch class."""

    def __init__(self, entity_id, device_id, device, name, state):
        """Initialize a sensor."""
        super().__init__()

        self.entity_id = entity_id
        self._device = device

        self._unique_id = device_id
        self._name = name
        self._state = state

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
    def is_on(self):
        """Return true if the switch is on."""
        return self._state

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    async def async_update(self):
        """Update the sensor state."""
        self._name = await self.hass.async_add_executor_job(
            getattr, self._device, "name"
        )
        self._state = await self.hass.async_add_executor_job(
            getattr, self._device, "state"
        )

        LOGGER.debug("Update switch state: %s = %s", self.entity_id, self._state)

    async def async_turn_on(self):
        """Turn the entity on."""
        await self.hass.async_add_executor_job(self._device.turn, True)
        self._state = True
        self.async_schedule_update_ha_state()

    async def async_turn_off(self):
        """Turn the entity off."""
        await self.hass.async_add_executor_job(self._device.turn, False)
        self._state = False
        self.async_schedule_update_ha_state()
