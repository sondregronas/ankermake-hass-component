"""
There is only one (hardcoded) select entity here, which is the video quality setting on the AnkerMake printers camera.
"""

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo

from . import AnkerMakeBaseEntity
from .ankerctl_util import VideoQuality, set_video_quality, AnkerUtilException
from .const import DOMAIN, MANUFACTURER
from .sensor_manifest import Description

_LOGGER = logging.getLogger(__name__)


class AnkerMakeSelectSensor(AnkerMakeBaseEntity, SelectEntity):
    _attr_options = list(VideoQuality.__members__.keys())
    _attr_current_option = VideoQuality.HD.name

    @callback
    def _update_from_anker(self) -> None:
        if self.coordinator.ankerdata.online:
            self._attr_available = True
        else:
            self._attr_available = False

    async def async_select_option(self, option: str) -> None:
        try:
            await set_video_quality(self.coordinator.config['host'], VideoQuality.__members__[option])
            self._attr_current_option = option
        except AnkerUtilException as e:
            _LOGGER.error(f"Failed to set video quality: {e}")


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    description = Description(
        key="quality",
        name="Video Quality",
        icon="mdi:quality-high"
    )
    dev_info = DeviceInfo(
        manufacturer=MANUFACTURER,
        identifiers={(DOMAIN, entry.entry_id)},
        name=coordinator.config["printer_name"])
    entity = AnkerMakeSelectSensor(coordinator, description, dev_info)
    async_add_entities([entity], True)
