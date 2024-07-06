"""
There is only one light on the AnkerMake printer, so the light entity will be a simple on/off switch and
is hardcoded in this file.
"""

import logging

from homeassistant.components.light import LightEntity
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo

from . import AnkerMakeBaseEntity
from .ankerctl_util import turn_on_light, turn_off_light, AnkerUtilException
from .const import DOMAIN, MANUFACTURER
from .sensor_manifest import Description

_LOGGER = logging.getLogger(__name__)


class AnkerMakeLightSensor(AnkerMakeBaseEntity, LightEntity):
    _attr_supported_color_modes = {"onoff"}
    _attr_color_mode = "onoff"
    _attr_is_on = False

    @callback
    def _update_from_anker(self) -> None:
        if self.coordinator.ankerdata.online:
            self._attr_available = True
        else:
            self._attr_available = False

    async def async_turn_on(self, **kwargs):
        try:
            await turn_on_light(self.coordinator.config['host'])
            self._attr_is_on = True
        except AnkerUtilException as e:
            _LOGGER.error(f"Failed to turn on light: {e}")

    async def async_turn_off(self, **kwargs):
        try:
            await turn_off_light(self.coordinator.config['host'])
            self._attr_is_on = False
        except AnkerUtilException as e:
            _LOGGER.error(f"Failed to turn on light: {e}")


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    description = Description(
        key="light",
        name="Light",
        icon="mdi:lightbulb"
    )
    dev_info = DeviceInfo(
        manufacturer=MANUFACTURER,
        identifiers={(DOMAIN, entry.entry_id)},
        name=coordinator.config["printer_name"])
    entity = AnkerMakeLightSensor(coordinator, description, dev_info)
    async_add_entities([entity], True)
