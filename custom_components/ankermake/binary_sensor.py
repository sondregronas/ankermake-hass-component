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
            self._attr_available = True
            self._attr_is_on = getattr(self.coordinator.ankerdata, self.entity_description.key)
        except (KeyError, AttributeError):
            _LOGGER.error(f"[AnkerMake] Sensor update failed")
            self._attr_available = False


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for description in BINARY_SENSOR_DESCRIPTIONS:
        dev_info = DeviceInfo(
            manufacturer=MANUFACTURER,
            identifiers={(DOMAIN, entry.entry_id)},
            name=coordinator.config["printer_name"])
        entities.append(AnkerMakeBinarySensor(coordinator, description, dev_info))
    async_add_entities(entities, True)
