from __future__ import annotations

import asyncio
import json
import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

from .ankermake_mqtt_adapter import AnkerData, AnkerException
from .const import DOMAIN, STARTUP

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up integration."""
    if DOMAIN in hass.data:
        _LOGGER.info("Delete ankermake from your yaml")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up zaptec as config entry."""

    _LOGGER.info(STARTUP)
    _LOGGER.debug("Setting up entry %s: %s", entry.entry_id, entry.data)

    coordinator = AnkerMakeUpdateCoordinator(
        hass,
        entry=entry,
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Setup all platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


class AnkerMakeUpdateCoordinator(DataUpdateCoordinator[None]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=5))

        self.config = entry.data
        self.ankerdata = AnkerData()
        self.entry = entry

        self._listen_to_ws_task = asyncio.create_task(self._listen_to_ws())

    async def _listen_to_ws(self):
        def on_message(message):
            try:
                self.ankerdata.update(message)
            except AnkerException:
                _LOGGER.error(f"[AnkerMake] Error updating data (Received message: {message})")

        session = aiohttp.ClientSession()
        async with session.ws_connect(self.config['host']) as ws:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    on_message(json.loads(msg.data))
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
        await session.close()

    async def _async_update_data(self):
        # Ensure task is still running
        if self._listen_to_ws_task.done():
            self._listen_to_ws_task = asyncio.create_task(self._listen_to_ws())
            await asyncio.sleep(5)  # If the task dies, wait 5 seconds before trying again


class AnkerMakeBaseEntity(CoordinatorEntity[AnkerMakeUpdateCoordinator]):
    def __init__(self, coordinator: AnkerMakeUpdateCoordinator,
                 description: EntityDescription, device_info: DeviceInfo):
        super().__init__(coordinator)
        self.coordinator = coordinator

        # self._attr_name = ankerobject.name
        self._attr_name = f"{device_info['name']} {description.name}"
        self.entity_description = description
        self._attr_unique_id = description.key
        self._attr_device_info = device_info

    @property
    def data(self):
        return self.coordinator.ankerdata

    @callback
    def _handle_coordinator_update(self) -> None:
        super()._handle_coordinator_update()
        self._update_from_anker()

    def _update_from_anker(self) -> None:
        """Update the entity. (Used by sensor.py)"""
