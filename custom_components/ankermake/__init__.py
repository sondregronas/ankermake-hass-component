"""
AnkerMake integration for Home Assistant.

Responsible for setting up the update coordinator and forwarding the config entry to the platforms.
There isn't much to do here, as the responsibility of setting up the entities is delegated to the platforms.
"""

from __future__ import annotations

import asyncio
import datetime
import json
import logging
from datetime import timedelta

import aiohttp
import pytz
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

from .anker_models import AnkerException
from .ankerctl_util import get_api_status
from .ankermake_mqtt_adapter import AnkerData
from .const import DOMAIN, STARTUP, UPDATE_FREQUENCY_SECONDS

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.LIGHT,
    Platform.SELECT,
    Platform.IMAGE,
    Platform.BUTTON
]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up integration."""
    if DOMAIN in hass.data:
        _LOGGER.info("Delete ankermake from your yaml")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ankermake as config entry."""

    _LOGGER.info(STARTUP)
    _LOGGER.debug("Setting up entry %s: %s", entry.entry_id, entry.data)

    tz = await hass.async_add_executor_job(pytz.timezone, hass.config.time_zone)
    coordinator = AnkerMakeUpdateCoordinator(
        hass,
        entry=entry,
        tz=tz
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Setup all platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


class AnkerMakeUpdateCoordinator(DataUpdateCoordinator[None]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, tz: datetime.tzinfo = None):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=UPDATE_FREQUENCY_SECONDS))

        self.config = entry.data
        self.ankerdata = AnkerData(_timezone=tz)
        self.entry = entry

        self._listen_to_ws_task = asyncio.create_task(self._listen_to_ws())

    async def _listen_to_ws(self):
        def on_message(message):
            try:
                self.ankerdata.update(message)
            except AnkerException:
                _LOGGER.error(f"[AnkerMake] Error updating data (Received message: {message})")

        session = aiohttp.ClientSession()
        try:
            async with session.ws_connect(f"{self.config['host']}/ws/mqtt") as ws:
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        on_message(json.loads(msg.data))
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        break
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break
        except Exception as e:
            _LOGGER.debug(f"[AnkerMake] Error connecting to WS: {e}")
        finally:
            await session.close()

    async def _async_update_data(self):
        try:
            self.ankerdata._api_status = await get_api_status(self.config['host'])
        except AnkerException as e:
            _LOGGER.debug(f"[AnkerMake] Error updating API data: {e}")
        # Ensure task is still running
        if self._listen_to_ws_task.done():
            self._listen_to_ws_task = asyncio.create_task(self._listen_to_ws())


class AnkerMakeBaseEntity(CoordinatorEntity[AnkerMakeUpdateCoordinator]):
    def __init__(self, coordinator: AnkerMakeUpdateCoordinator,
                 description: EntityDescription, device_info: DeviceInfo):
        super().__init__(coordinator)
        self.coordinator = coordinator

        self._attr_name = f"{device_info['name']} {description.name}"
        self.entity_description = description
        self._attr_unique_id = f"{device_info['name']}_{description.key}"
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

    def _filter_handler(self, key: str):
        def td_convert(seconds):
            return str(timedelta(seconds=seconds))

        if key.startswith('%%TD='):
            val = getattr(self.coordinator.ankerdata, key.split('=')[1])
            return td_convert(val)
        elif key.startswith('='):
            return key[1:]
        elif key.startswith('%SVC_ONLINE='):
            return self.coordinator.ankerdata.get_api_service_online(key.split('=')[1])
        elif key.startswith('%SVC_STATE='):
            return self.coordinator.ankerdata.get_api_service_status(key.split('=')[1])
        elif key.startswith('%VERSION='):
            return self.coordinator.ankerdata.get_api_version_value(key.split('=')[1])
        elif key.startswith('%CFG='):
            return self.coordinator.config[key.split('=')[1]]

        return getattr(self.coordinator.ankerdata, key)
