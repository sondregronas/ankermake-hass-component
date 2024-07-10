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

Download and install the component via hacs and reboot, then add the integration via the Home Assistant UI by searching
for "AnkerMake" or click the button below.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ankermake)

> Note: You can add as many instances as you'd like (but you will need an ankerctl instance configured for each
> printer).

## Adding a camera (WIP)

<details>

<summary>Click to expand!</summary>

> NOTE: This might not work for you YET! Also it isn't the most reliable feed. See PR/Draft in
> ankerctl: [here](https://github.com/Ankermgmt/ankermake-m5-protocol/pull/162)

## Using go2rtc

`go2rtc.yaml` (https://github.com/AlexxIT/go2rtc?tab=readme-ov-file#go2rtc-home-assistant-add-on)

```yaml
streams:
  Anker:
    - ffmpeg:http://ankerctl-ip:4470/video
```

<details>
<summary>Alt: Frigate config</summary>

Note: Frigate just runs go2rtc

`config.yml`

```yaml
go2rtc:
  streams:
    Anker:
      - "ffmpeg:http://ankerctl-ip:4470/video"
```

</details>

## Lovelace Card (Home Assistant)

Add WebRTC integration from HACS (https://github.com/AlexxIT/WebRTC?tab=readme-ov-file#installation)

Use either `http://<go2rtc_ip>:1984` or `http://<frigate_ip>:1984` when configuring the integration, reboot and add
a `Custom: WebRTC Camera` card to the dashboard:

```yaml
type: custom:webrtc-camera
url: Anker
```

</details>

## Dependencies

For this component to work, you will need an instance of [ankerctl](https://github.com/Ankermgmt/ankermake-m5-protocol)
running and working. Please refer to the ankerctl documentation for installation instructions.

**Alternatively you can try my fork of the ankerctl addon here: https://github.com/sondregronas/ankermgmt-hassio-addons
** - which includes a lot of changes from exsting pull requests. I recommend you create an automation to restart the
addon every 2 hours to avoid socket issues.

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fsondregronas%2Fankermgmt-hassio-addons)

> **NOTE:** This AddOn might not receive any updates when the main branch of ankerctl gets updated.

(The branch of ankerctl I'm
using: https://github.com/sondregronas/ankermake-m5-protocol/tree/patch-exiles-1.1-auto-restart-on-failure)

<details>
<summary>Click here for a docker-compose setup</summary>

You can use this `docker-compose.yml` file to start an instance of my fork of ankerctl. Note that the container is set
to restart every 2 hours as a workaround for some socket issues I've encountered, but isn't strictly necessary.

```yaml
services:
  ankerctl:
    container_name: ankerctl
    restart: unless-stopped
    build:
      context: https://github.com/sondregronas/ankermake-m5-protocol.git#patch-exiles-1.1-auto-restart-on-failure
    privileged: true
    # host-mode networking is required for pppp communication with the
    # printer, since it is an asymmetrical udp protocol.
    network_mode: host
    environment:
      - FLASK_HOST=0.0.0.0
      - FLASK_PORT=4470
    volumes:
      - ankerctl_vol:/root/.config/ankerctl
      - ./ankermake-m5-protocol/web/:/app/web

  # This container will restart the ankerctl container every 2 hours
  # as a temporary workaround for some socket issues.
  ankerctl_restarter:
    image: docker
    volumes: [ "/var/run/docker.sock:/var/run/docker.sock" ]
    # 2 hours = 7200 seconds
    command: [ "/bin/sh", "-c", "while true; do sleep 7200; docker restart ankerctl; done" ]
    restart: unless-stopped
volumes:
  ankerctl_vol:
```

</details>

## Known issues

There are probably many issues to list...

- Filament is just derived from the gcode name, which might not be accurate
- The state will be forgotten if home assistant restarts
- No camera support (but can be worked around using go2rtc, though PPPP crashes a lot - stable when it doesn't crash!)
- There are no ways to pause/stop a print
- There are (almost) no unit tests :(
- Logging is pretty much non-existent, documentation is a bit lacking
- ankerctl can crash sometimes, hindering the integration from working until it's restarted (restarting every 2hrs seems
  to work well for me)
- The API isn't added to the main branch of ankerctl yet (but it is in my fork - see above)

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
