import logging
from datetime import datetime

import aiohttp
from homeassistant.components.image import ImageEntity
from homeassistant.core import callback, HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo

from . import AnkerMakeBaseEntity
from .const import DOMAIN, MANUFACTURER
from .sensor_manifest import Description

_LOGGER = logging.getLogger(__name__)


class AnkerMakeImageSensor(AnkerMakeBaseEntity, ImageEntity):

    def __init__(self, coordinator, description, dev_info, hass: HomeAssistant):
        super().__init__(coordinator, description, dev_info)
        self._gcode_preview_url = ''
        ImageEntity.__init__(self, hass=hass)

    @callback
    def _update_from_anker(self) -> None:
        gcode_preview_url = self.coordinator.ankerdata.image
        if gcode_preview_url != self._gcode_preview_url:
            self._attr_image_last_updated = datetime.now()
        self._gcode_preview_url = gcode_preview_url
        self._attr_image_url = self._gcode_preview_url

        if self.coordinator.ankerdata.online:
            self._attr_available = True
        else:
            self._attr_available = False

    async def async_image(self) -> bytes | None:
        """Return image bytes."""
        async with aiohttp.ClientSession() as session:
            async with session.get(self._gcode_preview_url) as response:
                return await response.read()


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    description = Description(
        key="gcode_preview",
        name="Gcode Preview Image",
        icon="mdi:image"
    )
    dev_info = DeviceInfo(
        manufacturer=MANUFACTURER,
        identifiers={(DOMAIN, entry.entry_id)},
        name=coordinator.config["printer_name"])
    entity = AnkerMakeImageSensor(coordinator, description, dev_info, hass=hass)
    async_add_entities([entity], True)