"""Constants for switchbot_cloud."""
import logging

from homeassistant.components.cover import DOMAIN as COVER_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN

LOGGER = logging.getLogger(__package__)

# Base component constants
NAME = "SwitchBot Cloud"
DOMAIN = "switchbot_cloud"
VERSION = "0.0.3"
ISSUE_URL = "https://github.com/stuart-c/homeassistant-switchbot/issues"

SUPPORTED_PLATFORMS = [COVER_DOMAIN, SENSOR_DOMAIN, SWITCH_DOMAIN]


NEW_COVER = "covers"
NEW_SENSOR = "sensors"
NEW_SWITCH = "switches"


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
