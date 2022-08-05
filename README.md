# Bose-SoundTouch-API (boseapi)

![LastEdit](https://img.shields.io:/static/v1?label=LastEdit&message=07/31/2022&color=9cf)
![Status](https://img.shields.io:/static/v1?label=Status&message=DRAFT&color=orange)
![Platform](https://img.shields.io:/static/v1?label=Platforms&message=Linux|Windows&color=yellowgreen)

This small project/repository contains general information about how to analyze the firmware images provided by _`BOSE`_ and also implements commands to interact with these devices. The API and some basic usage examples are provided in the [api-documentation](https://bose-soundtouch-api.readthedocs.io).

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

