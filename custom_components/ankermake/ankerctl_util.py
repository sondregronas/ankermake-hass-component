"""
A simple utility module to control the light and video quality settings on the AnkerMake printer via ankerctls mqtt websocket.
"""

import json
from enum import Enum

import aiohttp

from .anker_models import AnkerException


class AnkerUtilException(AnkerException):
    pass


class VideoQuality(Enum):
    HD = 1
    SD = 0


async def _send_ctrl(ankerctl_ws_host: str, ctrl: str):
    url = f"{ankerctl_ws_host}/ws/ctrl"
    session = aiohttp.ClientSession()

    try:
        async with session.ws_connect(url) as ws:
            await ws.send_str(ctrl)
    except Exception as e:
        raise AnkerUtilException(e)
    finally:
        await session.close()


async def turn_on_light(ankerctl_ws_host: str):
    cmd = {'light': True}
    try:
        await _send_ctrl(ankerctl_ws_host, json.dumps(cmd))
    except AnkerUtilException as e:
        raise AnkerUtilException(f"Failed to turn on light: {e}")


async def turn_off_light(ankerctl_ws_host: str):
    cmd = {'light': False}
    try:
        await _send_ctrl(ankerctl_ws_host, json.dumps(cmd))
    except AnkerUtilException as e:
        raise AnkerUtilException(f"Failed to turn off light: {e}")


async def toggle_light(ankerctl_ws_host: str, from_state: bool):
    try:
        await {True: turn_off_light, False: turn_on_light}[from_state](ankerctl_ws_host)
    except AnkerUtilException as e:
        raise AnkerUtilException(f"Failed to turn {['off', 'on'][from_state]} light: {e}")


async def set_video_quality(ankerctl_ws_host: str, quality: VideoQuality = VideoQuality.HD):
    cmd = {'quality': quality.value}
    try:
        await _send_ctrl(ankerctl_ws_host, json.dumps(cmd))
    except AnkerUtilException as e:
        raise AnkerUtilException(f"Failed to set video quality: {e}")


async def reload_ankerctl(host: str):
    url = host.replace("ws://", "http://").replace("wss://", "https://")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{url}/api/ankerctl/server/reload") as response:
                if response.status != 200:
                    raise AnkerUtilException(f"Failed to reload ankerctl: {response.status}")
    except Exception as e:
        raise AnkerUtilException(f"Failed to reload ankerctl: {e}")


async def get_api_status(host: str):
    """Gets the status of the ankerctl api."""
    url = host.replace("ws://", "http://").replace("wss://", "https://")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{url}/api/ankerctl/status") as response:
                # TODO: Temporary if on the main branch of ankerctl
                if response.status == 404:
                    raise AnkerUtilException("Ankerctl API not found (not present in ankerctl yet)")
                if response.status != 200:
                    raise AnkerUtilException(f"Failed to get api status: {response.status}")
                return await response.json()
    except Exception as e:
        raise AnkerUtilException(f"Failed to get api status: {e}")
