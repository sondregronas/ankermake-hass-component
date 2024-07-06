import json
from enum import Enum

import aiohttp

from .ankermake_mqtt_adapter import AnkerException


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
        raise AnkerUtilException(f"Failed to send control message: {e}")
    finally:
        await session.close()


async def turn_on_light(ankerctl_ws_host: str):
    cmd = {'light': True}
    await _send_ctrl(ankerctl_ws_host, json.dumps(cmd))


async def turn_off_light(ankerctl_ws_host: str):
    cmd = {'light': False}
    await _send_ctrl(ankerctl_ws_host, json.dumps(cmd))


async def toggle_light(ankerctl_ws_host: str, from_state: bool):
    await {True: turn_off_light, False: turn_on_light}[from_state](ankerctl_ws_host)


async def set_video_quality(ankerctl_ws_host: str, quality: VideoQuality = VideoQuality.HD):
    cmd = {'quality': quality.value}
    await _send_ctrl(ankerctl_ws_host, json.dumps(cmd))
