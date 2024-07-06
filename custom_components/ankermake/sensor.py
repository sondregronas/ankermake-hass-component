import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo

from . import AnkerMakeBaseEntity
from .const import DOMAIN, MANUFACTURER
from .sensor_manifest import SENSOR_DESCRIPTIONS

_LOGGER = logging.getLogger(__name__)


class AnkerMakeSensor(AnkerMakeBaseEntity, SensorEntity):
    @callback
    def _update_from_anker(self) -> None:
        try:
            # TODO: Add multiple attributes to allow for consolidation of sensors
            value = getattr(self.coordinator.ankerdata, self.entity_description.key)
            self._attr_available = True
            # Only update the value if it is not None (keep the old value)
            if value:
                self._attr_native_value = value
        except (KeyError, AttributeError):
            _LOGGER.error(f"[AnkerMake] Sensor update failed")
            self._attr_available = False


async def async_setup_entry(hass, entry, async_add_entities):
    # TODO: Consolidate sensor (i.e. Hot End Temperature includes both current and target)
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for description in SENSOR_DESCRIPTIONS:
        dev_info = DeviceInfo(
            manufacturer=MANUFACTURER,
            identifiers={(DOMAIN, entry.entry_id)},
            name=coordinator.config["printer_name"])
        entities.append(AnkerMakeSensor(coordinator, description, dev_info))
    async_add_entities(entities, True)
