"""
AnkerMake binary sensor platform for Home Assistant. Sensors are generated via sensor_manifest.py and are updated
via the _update_from_anker method.
"""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo

from . import AnkerMakeBaseEntity
from .const import DOMAIN, MANUFACTURER
from .sensor_manifest import BINARY_SENSOR_DESCRIPTIONS

_LOGGER = logging.getLogger(__name__)


class AnkerMakeBinarySensor(AnkerMakeBaseEntity, BinarySensorEntity):
    @callback
    def _update_from_anker(self) -> None:
        try:
            self._attr_is_on = getattr(self.coordinator.ankerdata, self.entity_description.key)

            if self.coordinator.ankerdata.online:
                self._attr_available = True
            else:
                self._attr_available = False
        except AttributeError:
            self._attr_available = False


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    dev_info = DeviceInfo(
        manufacturer=MANUFACTURER,
        identifiers={(DOMAIN, entry.entry_id)},
        name=coordinator.config["printer_name"])

    for description in BINARY_SENSOR_DESCRIPTIONS:
        entities.append(AnkerMakeBinarySensor(coordinator, description, dev_info))

    async_add_entities(entities, True)
