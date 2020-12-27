"""Sensor platform for switchbot_cloud."""
from datetime import timedelta
from homeassistant.components.sensor import ENTITY_ID_FORMAT
from homeassistant.const import DEVICE_CLASS_BATTERY, PERCENTAGE
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import async_generate_entity_id, Entity

from .account import get_account_from_config_entry
from .const import DOMAIN, LOGGER, NAME, NEW_SENSOR, VERSION

SCAN_INTERVAL = timedelta(minutes=5)
PARALLEL_UPDATES = 1


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up a sensors for SwitchBot Cloud."""
    account = get_account_from_config_entry(hass, config_entry)

    LOGGER.debug("Setup sensors for %s", account.username)

    @callback
    def async_add_sensor(devices):
        entities = []

        for parent_device in devices:
            parent_id = parent_device.id
            parent_name = parent_device.name
            children = parent_device.children

            if not children:
                children = [parent_device]

            for device in children:
                device_id = device.id
                name = device.name
                battery = device.battery

                if device_id in account.known_ids[NEW_SENSOR]:
                    continue

                entity_id = async_generate_entity_id(
                    ENTITY_ID_FORMAT, "{} battery level".format(name), hass=hass
                )

                LOGGER.debug("Initialize %s", entity_id)

                entities.append(
                    SwitchBotCloudBatterySensor(
                        entity_id,
                        device_id,
                        device,
                        name,
                        parent_id,
                        parent_device,
                        parent_name,
                        battery,
                    )
                )

                account.known_ids[NEW_SENSOR].append(device_id)

        if entities:
            async_add_entities(entities)

    account.listeners.append(
        async_dispatcher_connect(
            hass, account.async_signal_new_device(NEW_SENSOR), async_add_sensor
        )
    )


class SwitchBotCloudBatterySensor(Entity):
    """A battery sensor implementation for SwitchBot Cloud."""

    def __init__(
        self,
        entity_id,
        device_id,
        device,
        name,
        parent_id,
        parent_device,
        parent_name,
        battery,
    ):
        """Initialize a sensor."""
        super().__init__()

        self.entity_id = entity_id
        self._device = device

        self._unique_id = "{}_battery_level".format(device_id)
        self._name = name
        self._battery = battery

        self._parent = parent_device
        self._parent_id = parent_id
        self._parent_name = parent_name

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def device_info(self):
        """Device info."""
        return {
            "identifiers": {(DOMAIN, self._parent_id)},
            "name": self._parent_name,
            "manufacturer": NAME,
            "model": VERSION,
        }

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._battery

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_class(self):
        """Return the class of the sensor."""
        return DEVICE_CLASS_BATTERY

    @property
    def unit_of_measurement(self):
        """Return the units of measurement."""
        return PERCENTAGE

    async def async_update(self):
        """Update the sensor state."""
        self._name = await self.hass.async_add_executor_job(
            getattr, self._device, "name"
        )
        self._battery = await self.hass.async_add_executor_job(
            getattr, self._device, "battery"
        )

        self._parent_name = await self.hass.async_add_executor_job(
            getattr, self._parent, "name"
        )

        LOGGER.debug(
            "Update battery sensor state: %s = %s", self.entity_id, self._battery
        )
