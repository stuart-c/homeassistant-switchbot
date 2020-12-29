"""Cover platform for switchbot_cloud."""
from .const import DEFAULT_NAME, DOMAIN, ICON, COVER
from .entity import SwitchBotCloudEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup cover platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([SwitchBotCloudCover(coordinator, entry)])


class SwitchBotCloudCover(SwitchBotCloudEntity):
    """switchbot_cloud Cover class."""

    @property
    def name(self):
        """Return the name of the cover."""
        return f"{DEFAULT_NAME}_{COVER}"

    @property
    def state(self):
        """Return the state of the cover."""
        return self.coordinator.data.get("body")

    @property
    def icon(self):
        """Return the icon of the cover."""
        return ICON
