# Bose-SoundTouch-API (boseapi)

![LastEdit](https://img.shields.io:/static/v1?label=LastEdit&message=03/06/2023&color=9cf)
![Status](https://img.shields.io:/static/v1?label=Status&message=DRAFT&color=orange)
![Platform](https://img.shields.io:/static/v1?label=Platforms&message=Linux|Windows&color=yellowgreen)
![PyPi](https://img.shields.io:/static/v1?label=PyPi&message=0.2.0&color=green)

This small project implements commands to interact with these devices. The API and some basic usage examples are provided in the [api-documentation](https://bose-soundtouch-api.readthedocs.io).

## Installation

This module can be easily installed via pip:
```bash
$ python3 -m pip install boseapi
```

## Usage

```python
from boseapi.all import *

device = new_device('127.0.0.1')
client = SoundTouchClient(device, errors='ignore')

# fetch device's capabilities
capabilities = client.capabilities()
if capabilities.wsapiproxy:
      # Create and use a WebSocket client
      ws_client = BoseWebSocket(device)
      # Add a listener on an updated volume
      ws_client.add_listener(nodes.volumeupdated, lambda xmlelement: print(xmlelement.tag))
      ws_client.start_notification()

# Get the current volume and appply a new value to it (0..100).
volume = client.volume()
# client.set_volume(7)
# client.set_volume(volume.actual_vol + 1) 
# has the same effect as
client.volume_up()

# If media is currently played by the device:
status = client.status()
if status.play_status != 'PLAY_STATE':
      # Play own media
      item = ContentItem(src=Source.INTERNET_RADIO, location='4712')
      client.play(item)

# Load and select presets
presets = client.listpresets()
if len(presets) > 0:
      preset = presets[0]
      client.select_preset(preset)

# Multiroom functionality
current_zone = client.zone_status()
if current_zone.masterid == None:
      zone = Zone(device_id=device.device_id, ip=device.host)
      
      # Add different zone slaves (it is recommended to create new devices
      # befor adding a zone slave.
      device2 = boseapi.new_device('127.0.0.2')
      slave = ZoneSlave(device_id=device2.device_id, ip_address=device2.host)
      zone.append(slave)

      # Create zone/ Add slaves/ Remove slaves
      client.create_zone(zone)
      client.remove_zone_slave([slave])
      client.add_zone_slave([slave])

# List all available UPnP MediaServers
media_servers = client.media_servers()
if len(media_servers) > 0:
for server in media_servers:
      print(server)

# List all available sources
sources = client.listsources()
if len(sources) > 0:
# Get specific source items with the source name
source_item = sources['QPLAY']
# or the index position
source_item2 = sources[0]

# Select different input sources
client.select_source(Source.BLUETOOTH)

if source_item.status == 'READY':
      client.select_source(source_item.source)

# make sure the node is available be fore fetching data
if 'GET' in client.options(nodes.bass):
      # manually fetch or set data
      message = client.get(nodes.bass)
      bass = Bass(message.response)
      client.put(nodes.bass, '<bass>0</bass>')
```

## Overview
---
Starting off with the used device and app to get the information used to write the code for this repository.

> `Bose SoundTouch 300` and the `SoundTouch` app by BOSE

While capturing traffic of the BOSE device the following URL was requested when searching for a sofware update:

      > https://downloads.bose.com/updates/soundtouch

The request is forwarded to another backend which contains a XML-Document named `index.xml`. This file contains information about the locations of all available firmware upgrades. Since the device used here needs the `SoundTouch 30` firmware, the following link is used.

      > https://downloads.bose.com/ced/soundtouch/mr4_cdb9ab51/Update_ti_27.0.3.46298.4608935.scm.stu

After downloading, a quick review with binwalk on the file:

```console
$ binwalk Update_ti_27.0.3.46298.4608935.scm.stu                                                 

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
312           0x138           ELF, 32-bit LSB executable, ARM, version 1 (SYSV)
[...]
13932404      0xD49774        UBI erase count header, version: 1, EC: 0x0, VID header offset: 0x800, data offset: 0x1000
[...]
```

The only interesting line in the binwalk output contains information about an UBI image header. So, extract that file and decompress it with `ubidump`:

```console
$ ubidump -s . D49774.ubi
```

This command creates a folder in the current directory where all the contents of this UBI document are stored. Files that contain information usable for creating this API are located in the following directory: `rootfs/opt/Bose/etc/`.

There are two files that configure operations that can be requested/ executed on the webserver (port `8090`). All operations contained in:

```bash
rootfs/opt/Bose/etc/HandCraftedWebServer-SoundTouch.xml 
# and
rootfs/opt/Bose/etc/WebServer-SoundTouch.xml
```

were implemented in this small library.

---
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->
---
## License

Distributed under the MIT License. See `MIT.txt` for more information.

