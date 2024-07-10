"""
AnkerMake sensor platform for Home Assistant. Sensors are generated via sensor_manifest.py and are updated via the
_update_from_anker method.
"""

import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo

from . import AnkerMakeBaseEntity
from .const import DOMAIN, MANUFACTURER
from .sensor_manifest import SENSOR_DESCRIPTIONS, SENSOR_WITH_ATTR_DESCRIPTIONS

_LOGGER = logging.getLogger(__name__)


class AnkerMakeSensor(AnkerMakeBaseEntity, SensorEntity):
    @callback
    def _update_from_anker(self) -> None:
        try:
            value = self._filter_handler(self.entity_description.key)
            if self.coordinator.ankerdata.online:
                self._attr_available = True
            else:
                self._attr_available = False
            # Only update the value if it is not None (keep the old value)
            if value:
                self._attr_native_value = value
        except AttributeError:
            self._attr_available = False


class AnkerMakeSensorWithAttr(AnkerMakeBaseEntity, SensorEntity):
    def __init__(self, coordinator, description, dev_info, attrs):
        super().__init__(coordinator, description, dev_info)
        self.attrs = attrs.copy()
        self._attr_extra_state_attributes = dict()

    @callback
    def _update_from_anker(self) -> None:
        try:
            self._attr_native_value = self._filter_handler(self.attrs['state'])

            for attr, key in self.attrs.items():
                if attr == 'state':
                    continue
                self._attr_extra_state_attributes[attr] = self._filter_handler(key)

            if not self.coordinator.ankerdata.online:
                self._attr_available = True
            else:
                self._attr_available = False
        except (AttributeError, KeyError):
            self._attr_available = False


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    dev_info = DeviceInfo(
        manufacturer=MANUFACTURER,
        identifiers={(DOMAIN, entry.entry_id)},
        name=coordinator.config["printer_name"])

    for description in SENSOR_DESCRIPTIONS:
        entities.append(AnkerMakeSensor(coordinator, description, dev_info))
    for description, attributes in SENSOR_WITH_ATTR_DESCRIPTIONS:
        entities.append(AnkerMakeSensorWithAttr(coordinator, description, dev_info, attributes))

    async_add_entities(entities, True)
