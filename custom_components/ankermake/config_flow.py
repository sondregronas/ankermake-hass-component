"""
AnkerMake Config Flow
- host: str (will be ws(s)://<host>)
- printer_name: str (the device name)
"""

import re

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

VOL_SCHEME = vol.Schema({
    vol.Required("host", default="<ankerctl_ip>:4470"): vol.Coerce(str),
    vol.Required("printer_name", default="AnkerMake M5"): vol.Coerce(str),
})


class AnkerMakeFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for AnkerMake."""
    VERSION = 1

    async def async_step_user(self, user_input: ConfigType = None):
        # If the user input is empty, show the form
        if not user_input:
            return self.async_show_form(step_id="user", data_schema=VOL_SCHEME)

        # Replace http(s) with ws(s)
        host = user_input["host"].replace('http://', 'ws://').replace('https://', 'wss://')
        # Ensure the host is in the correct format (ws:// or wss://)
        if not re.match(r"wss?://.+(:\d+)?", host):
            host = f"ws://{host}"
        # Ensure there is no trailing slashes or paths
        host = re.search(r'(wss?://[^/]+)', host).group(1)

        # Update the user input
        user_input["host"] = host

        # Ensure host is unique
        unique_id = user_input["printer_name"]
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title=user_input['printer_name'], data=user_input)
