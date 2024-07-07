NAME = 'AnkerMake'
VERSION = '0.4.0'
ISSUEURL = 'https://github.com/sondregronas/ankermake-hass-component/issues'

DOMAIN = 'ankermake'
MANUFACTURER = 'Anker'

STARTUP = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom component
If you have any issues with this you need to open an issue here:
{ISSUEURL}
-------------------------------------------------------------------
"""

UPDATE_FREQUENCY_SECONDS = 5
