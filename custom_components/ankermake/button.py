"""
There is only one (hardcoded) entity here, which is the reload ankerctl button.
"""

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.core import callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.device_registry import DeviceInfo

from . import AnkerMakeBaseEntity
from .ankerctl_util import AnkerUtilException, reload_ankerctl
from .const import DOMAIN, MANUFACTURER
from .sensor_manifest import Description

_LOGGER = logging.getLogger(__name__)


class AnkerMakeButtonSensor(AnkerMakeBaseEntity, ButtonEntity):
    @callback
    def _update_from_anker(self) -> None:
        if self.coordinator.ankerdata.online:
            self._attr_available = True
        else:
            self._attr_available = False

    async def async_press(self) -> None:
        try:
            await reload_ankerctl(self.coordinator.config['host'])
        except AnkerUtilException as e:
            raise ServiceValidationError(e)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    description = Description(
        key="reload_ankerctl",
        name="Reload ankerctl",
        icon="mdi:reload",
    )
    dev_info = DeviceInfo(
        manufacturer=MANUFACTURER,
        identifiers={(DOMAIN, entry.entry_id)},
        name=coordinator.config["printer_name"])
    entity = AnkerMakeButtonSensor(coordinator, description, dev_info)
    async_add_entities([entity], True)
