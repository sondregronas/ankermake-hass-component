# AnkerMake Home Assistant Component

[![Validation](https://github.com/sondregronas/ankermake-hass-component/actions/workflows/hassfest.yml/badge.svg)](https://github.com/sondregronas/ankermake-hass-component/actions/workflows/hassfest.yml)
[![Tests](https://github.com/sondregronas/ankermake-hass-component/actions/workflows/tests.yml/badge.svg)](https://github.com/sondregronas/ankermake-hass-component/actions/workflows/tests.yml)
[![Release](https://github.com/sondregronas/ankermake-hass-component/actions/workflows/release.yml/badge.svg)](https://github.com/sondregronas/ankermake-hass-component/actions/workflows/release.yml)
![Downloads total](https://img.shields.io/github/downloads/sondregronas/ankermake-hass-component/total)
![Downloads latest](https://img.shields.io/github/downloads/sondregronas/ankermake-hass-component/latest/total)

Ever wanted a quick way to check the status of your AnkerMake M5 3D printer? This Home Assistant component allows you to
do just that! It listens to the mqtt socket of an [ankerctl](https://github.com/Ankermgmt/ankermake-m5-protocol)
instance and updates the status of your printer in real-time.

<img src=".github/media/device_view.png" width="70%">

> Note: There are a lot of hidden entities in the image above, which are mostly set as attributes of the displayed
> entities, such as the current print time, the current layer, the current print progress, the current print time left,
> etc.


`3D Printer state changes to Finished -> Flash some pretty lights -> Hotend temperature is below 40C for 60 minutes -> Disconnect printer from power!`

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=sondregronas&repository=ankermake-hass-component&category=ankermake)

Download and install the component via hacs (alternatively copy the contents of the latest release into
`custom_components/ankermake` folder to your Home Assistant instance) and reboot, then add the integration via the
Home Assistant UI by searching for "AnkerMake" or click the button below.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ankermake)

> Note: You can add as many instances as you'd like (but you will need an ankerctl instance running for each one).

## Dependencies

For this component to work, you will need an instance of [ankerctl](https://github.com/Ankermgmt/ankermake-m5-protocol)
running and working. Please refer to the ankerctl documentation for installation instructions. (They do have a Home
Assistant add-on in their organization, but I have not tested it with this component).

## Known issues

There are probably many issues to list...

- Filament is just derived from the gcode name, which might not be accurate
- There's probably an easier way to not poll the mqtt socket (requesting from the printer, right now it just listens on
  a separate thread)
- The state will be forgotten if home assistant restarts
- Config flow will not verify the connection to the ankerctl instance (it will just assume it's correct)
- No camera support (but can be worked around using go2rtc, though PPPP crashes a lot - stable when it doesn't crash!)
- There are no ways to pause/stop a print
- There are (almost) no unit tests :(
- Logging is pretty much non-existent, documentation is a bit lacking
- ankerctl can crash sometimes, hindering the integration from working until it's restarted

## Testing

This component might be unstable! Please report any issues you encounter. I have barely tested it.

## Development

Contributions are very welcome!

The easiest way to add new sensors is by editing
the [sensor_manifest.py](./custom_components/ankermake/sensor_manifest.py)
and [ankermake_mqtt_adapter.py](./custom_components/ankermake/ankermake_mqtt_adapter.py) files. The latter file converts
the published mqtt messages to a `AnkerData` object which corresponds to the `key` in the `sensor_manifest.py` file.

The `docker-compose.yml` file can be used to start a local home assistant instance with the component installed.

## Legal

This project is NOT endorsed, affiliated with, or supported by Anker.
