"""Sensor platform for switchbot_cloud."""
from .const import DEFAULT_NAME, DOMAIN, ICON, SENSOR
from .entity import SwitchBotCloudEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([SwitchBotCloudSensor(coordinator, entry)])


class SwitchBotCloudSensor(SwitchBotCloudEntity):
    """switchbot_cloud Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_{SENSOR}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("body")

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON
