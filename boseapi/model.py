# MIT License
#
# Copyright (c) 2023 MatrixEditor
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from typing import Iterator
from xml.etree.ElementTree import Element, tostring


def _xmlfind_attr(root: Element, tag: str, name: str, default = None):
    return _xmlfind(root, tag, lambda x: x.get(name, default), default)


def _xmlfind(root: Element, tag: str, extractor = lambda x: x.text, default = None):
    if not root:
        return default

    result = root.find(tag)
    if result is None:
        return default
    return extractor(result)


class Volume:
    """A class representing the current Volume config."""

    def __init__(self, root: Element = None, actual_vol: int = 0,
                target_vol: int = 0, muted: bool = False) -> None:
        self.actual_vol = int(_xmlfind(root, 'actualvolume', default='0')) if root else actual_vol
        self.target_vol = int(_xmlfind(root, 'targetvolume', default='0')) if root else target_vol
        self.muted = _xmlfind(root, 'muteenabled', default='false') == 'true' if root else muted

    @property
    def actualvolume(self) -> int:
        """The actual volume value."""
        return self.actual_vol

    @property
    def targetvolume(self) -> int:
        """A volume value which will be targeted."""
        return self.target_vol

    def is_muted(self) -> bool:
        """Returns whether the device is muted."""
        return self.muted

    @staticmethod
    def body(level: int) -> str:
        """Returns the POST body for changing the current volume."""
        return '<volume>%d</volume>' % level

    def __repr__(self) -> str:
        return '<Volume actual=%d, target=%d, muted=%s>' % (self.actualvolume, self.targetvolume, self.is_muted())


class ZoneSlave:
    """A class representing a multiroom slave."""
    def __init__(self, root: Element = None, ip_address: str = None,
                role: str = None, device_id: str = None) -> None:
        self.ip_address = root.get('ipaddress') if root else ip_address
        self.role = root.get('role') if root else role
        self._device_id = None if root else device_id

    @property
    def deviceid(self) -> str:
        """The stored device id."""
        return self._device_id

    @property
    def ipaddress(self) -> str:
        """The ip address this slave belongs to."""
        return self.ip_address

    @property
    def devicerole(self) -> str:
        """An optional role for that device."""
        return self.role

    def __repr__(self) -> str:
        return '<ZoneSlave dev_id="%s", ip="%s", role="%s">' % (
        self.deviceid, self.ipaddress, self.devicerole
        )


class Zone:
    """A class representing a mutliroom master.

    This class contains a list-like implementation to store the different
    ZoneSlaves.
    """

    def __init__(self, root: Element = None, device_id: str = None,
                ip: str = None, slaves: list = None) -> None:
        self.master_id = _xmlfind_attr(root, 'zone', 'master') if root else device_id
        self.master_ip = _xmlfind_attr(root, 'zone', 'senderIPAddress') if root else ip
        self.slaves = [] if not slaves else slaves

        for slave in root.findall('member'):
            self.slaves.append(ZoneSlave(slave))

    @property
    def masterid(self) -> str:
        """The master id."""
        return self.master_id

    @property
    def masterip(self) -> str:
        "The master ip address."
        return self.master_ip

    def to_xml(self) -> str:
        """Converts this object into a xml representation."""
        xmlstr = '<zone master="%s" senderIPAddress="%s">' % (self.master_id, self.master_ip)
        for slave in self:
            xmlstr = '%s<member ipaddress="%s">%s</member>' % (xmlstr, slave.ipaddress, slave.deviceid)
        return '%s</zone>' % xmlstr

    def is_zone_master(self) -> bool:
        """Returns whether this zone object is a zone master."""
        return self.master_ip is None

    def __iter__(self) -> Iterator:
        return iter(self.slaves)

    def __len__(self) -> int:
        return len(self.slaves)

    def __getitem__(self, key) -> ZoneSlave:
        if isinstance(key, int) and 0 <= key < len(self):
            return self.slaves[key]

    def __setitem__(self, key, value):
        if isinstance(key, int) and 0 <= key < len(self):
            self.slaves[key] = value

    def append(self, slave: ZoneSlave):
        """Adds a new slave to the stored ones (only if slave != None)."""
        if slave: self.slaves.append(slave)


class InfoNetworkConfig:
    """An object storing basic attributes of device's connected interfaces."""
    def __init__(self, root: Element) -> None:
        self._net_type = root.get('type')
        self._net_mac = _xmlfind(root, 'macAddress')
        self._net_ip = _xmlfind(root, 'ipAddress')

    @property
    def macaddress(self) -> str:
        """The device's mac address."""
        return self._net_mac

    @property
    def nettype(self) -> str:
        """The adapter type (WIFI or ETHERNET)."""
        return self._net_type

    @property
    def ipaddress(self) -> str:
        """The mapped ip address."""
        return self._net_ip

    def __repr__(self) -> str:
        return '<NetConfigInfo ip="%s", mac="%s", type="%s">' % (
        self.ipaddress, self.macaddress, self.nettype
        )


class Status:
    """A class covering all information about the current ContentItem.

    An object of this class can be obtained when querying the nowPlaying
    node.
    """

    def __init__(self, root: Element) -> None:
        self._source = _xmlfind_attr(root, 'nowPlaying', 'source')

        self._content_item = None
        content_item = root.find("ContentItem")
        if content_item: self._content_item = ContentItem(root=content_item)

        self._track = _xmlfind(root, "track")
        self._artist = _xmlfind(root, "artist")
        self._album = _xmlfind(root, "album")
        image_status = _xmlfind_attr(root, "art", "artImageStatus")
        if image_status == "IMAGE_PRESENT": self._image = _xmlfind(root, "art")
        else: self._image = None

        self._duration = int(_xmlfind_attr(root, "time", "total", default='0'))
        self._position = int(_xmlfind(root, "time", default='0'))
        self._play_status = _xmlfind(root, "playStatus")
        self._shuffle_setting = _xmlfind(root, "shuffleSetting")
        self._repeat_setting = _xmlfind(root, "repeatSetting")
        self._stream_type = _xmlfind(root, "streamType")
        self._track_id = _xmlfind(root, "trackID")
        self._station_name = _xmlfind(root, "stationName")
        self._description = _xmlfind(root, "description")
        self._station_location = _xmlfind(root, "stationLocation")

    @property
    def source(self) -> str:
        """The media source: should be one of the sources defined in boseapi.common.source"""
        return self._source

    @property
    def contentitem(self) -> 'ContentItem':
        """The selected ContentItem."""
        return self._content_item

    @property
    def track(self) -> str:
        """If present, the current media file name."""
        return self._track

    @property
    def artist(self) -> str:
        """If present, the creator of the track."""
        return self._artist

    @property
    def album(self) -> str:
        """If present, the album of the playing track."""
        return self._album

    @property
    def image(self) -> str:
        """If present, a link/URL to the cover image of the track."""
        return self._image

    @property
    def duration(self) -> str:
        """The track's duration."""
        return self._duration

    @property
    def position(self) -> str:
        return self._position

    @property
    def play_status(self) -> str:
        """Indicates whether the device is currently playing the embedded track."""
        return self._play_status

    @property
    def shuffle_setting(self) -> bool:
        """True, if shuffle is enabled, false otherwise."""
        return self._shuffle_setting

    @property
    def repeat_setting(self) -> bool:
        """True, if repeat is enabled, false otherwise."""
        return self._repeat_setting

    @property
    def streamtype(self) -> str:
        """The stream type of the current track (TRACK_ONDEMAND when playing from
        an external resource)."""
        return self._stream_type

    @property
    def trackid(self) -> str:
        """The track's id."""
        return self._track_id

    @property
    def station(self) -> str:
        """If present, the station's name."""
        return self._station_name

    @property
    def description(self) -> str:
        """If present, this property contains a brief description that was added
        to the track."""
        return self._description

    @property
    def stationlocation(self) -> str:
        """The station's location."""
        return self._station_location


class ContentItem:
    """A class covering all information about the media source.

    Instances of this class can be used to switch the input source of media.
    """

    def __init__(self, src: str = None, account: str = None, media_type: str = None,
                location: str = None, root: Element = None, name: str = None) -> None:
        self._name = _xmlfind(root, "itemName") if root else name
        self._source = root.get("source") if root else src
        self._type = root.get("type") if root else media_type
        self._location = root.get("location") if root else location
        self._source_account = root.get("sourceAccount") if root else account
        self._is_presetable = root.get("isPresetable") == 'true' if root else True

    @property
    def xml_str(self) -> str:
        """The item object as an XML string."""
        xml = '<ContentItem '
        if self.source: xml = '%ssource="%s" ' % (xml, self.source)
        if self.sourceaccount: xml = '%ssourceAccount="%s" ' % (xml, self.sourceaccount)
        if self.location: xml = '%slocation="%s" ' % (xml, self.location)
        if self.itemtype: xml = '%stype="%s" ' % (xml, self.itemtype)
        if not self.name:
            return '%s/>' % xml
        else:
            return '%s><itemName>%s</itemName></ContentItem>' % (xml, self.name)

    @property
    def name(self) -> str:
        """The item's name."""
        return self._name

    @property
    def source(self) -> str:
        """The media source type. This value is defined at `boseapi.common.source`."""
        return self._source

    @property
    def itemtype(self) -> str:
        """Specifies the type of this item."""
        return self._type

    @property
    def location(self) -> str:
        """If present, a direct link to the media."""
        return self._location

    @property
    def sourceaccount(self) -> str:
        """The source account this content item is played with."""
        return self._source_account

    def is_presetable(self) -> bool:
        """Returns True if this content item can be saved as a Preset."""
        return self._is_presetable

    def __repr__(self):
        return '<ContentItem source="%s", isPresetable=%s>' % (self.source, self.is_presetable())


class SimpleConfig:
    """A class used to represent single node XML-response.

    On init, this object takes all stored attributes and the text from
    an XML-Element.
    """
    def __init__(self, root: Element) -> None:
        self._tag = root.tag
        self._value = root.text
        self._attr = root.attrib

    @property
    def attrib(self) -> dict:
        """The stored attributes. (Only 'bearertoken' uses them)"""
        return self._attr

    @property
    def configname(self) -> str:
        """The XML tag name."""
        return self._tag

    @property
    def value(self) -> str:
        """The stored text value from the XML-Element."""
        return self._value

    @staticmethod
    def body(tag: str, value) -> str:
        return '<%s>%s</%s>' % (tag, value, tag)

    def __repr__(self) -> str:
        _name = '%s%s' % (self.configname[1].upper(), self.configname[1:])
        return '<%s value="%s" attrib=%s>' % (_name, self.value, self.attrib)


class Bass:
    """The current bass configuration."""

    def __init__(self, root: Element) -> None:
        self._target_bass = int(_xmlfind(root, 'targetbass', default=0))
        self._actual_bass = int(_xmlfind(root, 'actualbass', default=0))

    @property
    def target(self) -> int:
        """A value representing the targeted bass."""
        return self._target_bass

    @property
    def actual(self) -> int:
        """A value representing the actual bass value."""
        return self._actual_bass

    @staticmethod
    def body(level: int) -> str:
        """Returns the XML-Body to change the bass value."""
        return '<bass>%s</bass>' % level

    def __repr__(self) -> str:
        return '<Bass target=%d, actual=%d>' % (self.target, self.actual)


class BassCapabilities:
    """A simple boolean value wrapper.

    This class stores True if bass capabilities are enabled on the BOSE device.
    """

    def __init__(self, root: Element) -> None:
        self._available = _xmlfind(root, 'bassAvailable', default='false') == 'true'

    @property
    def available(self) -> bool:
        """Returns whether bass capabilities are enabled on that device."""
        return self._available

    def __repr__(self) -> str:
        return '<BassCapabilities available=%s>' % self.available


class Balance:
    """A class to represent the balance configuration."""

    def __init__(self, root: Element) -> None:
        self._balanceAvailable = _xmlfind(root, 'balanceAvailable', default='false') == 'true'
        self._balanceMin = int(_xmlfind(root, 'balanceMin', default=0))
        self._balanceMax = int(_xmlfind(root, 'balanceMax', default=0))
        self._balanceDefault = int(_xmlfind(root, 'balanceDefault', default=0))
        self._targetBalance = int(_xmlfind(root, 'targetBalance', default=0))
        self._actualBalance = int(_xmlfind(root, 'actualBalance', default=0))

    @property
    def available(self) -> bool:
        """True, if a balance fconfiiguration can be altered."""
        return self._balanceAvailable

    @property
    def min(self) -> int:
        """The minimum of balance."""
        return self._balanceMin

    @property
    def max(self) -> int:
        """The maximum of balance."""
        return self._balanceMax

    @property
    def default(self) -> int:
        """The default balance value."""
        return self._balanceDefault

    @property
    def target(self) -> int:
        """The targeted value of balance."""
        return self._targetBalance

    @property
    def actual(self) -> int:
        """The actual value of balance."""
        return self._actualBalance

    def __repr__(self) -> str:
        if not self.available:
            return '<Balance available=False>'
        else:
            return '<Balance min=%d, max=%d, default=%d, target=%d, actual=%d>' % (
                self.min, self.max, self.default, self.actual, self.target
            )


class Capabilities:
    """The global capabilities storage.

    This class contains important configuration values, such as `wsapiproxy`
    which indicates whether the WebSocket notification API can be used.

    Next, a capabilities object shows whether a clock display is available
    or the device can run in `dualMode`. Each device comes along with different
    additional features, which are also stored in this class with a dict-like
    implementation with the following mapping: `self[cap.name] = cap.url`.
    """
    def __init__(self, root: Element) -> None:
        self._lightswitch = _xmlfind(root, 'lightswitch', default='false') == 'true'
        self._clockDisplay = _xmlfind(root, 'clockDisplay', default='false') == 'true'
        self._lrStereoCapable = _xmlfind(root, 'lrStereoCapable', default='false') == 'true'
        self._bcoresetCapable = _xmlfind(root, 'bcoresetCapable', default='false') == 'true'
        self._disablePowerSaving = _xmlfind(root, 'disablePowerSaving', default='false') == 'true'
        self._dualMode = _xmlfind(root, './networkConfig/dualMode', default='false') == 'true'
        self._wsapiproxy = _xmlfind(root, './networkConfig/wsapiproxy', default='false') == 'true'
        self._capabilities = {}

        for cap in root.findall('capability'):
            self[cap.get('name')] = cap.get('url')

    def __getitem__(self, key):
        return self._capabilities[key]

    def __setitem__(self, key, value):
        self._capabilities[key] = value

    def __iter__(self) -> Iterator:
        return iter(self._capabilities)

    def __len__(self) -> int:
        return len(self._capabilities)

    @property
    def lightswitch(self):
        """Returns whether the lightswitch can be used."""
        return self._lightswitch

    @property
    def clockDisplay(self):
        """Returns whether the clock display is available."""
        return self._clockDisplay

    @property
    def lrStereoCapable(self):
        """Returns whether the device is left-right stereo capable."""
        return self._lrStereoCapable

    @property
    def bcoresetCapable(self):
        """Returns whether the device contains a BOSE coreset."""
        return self._bcoresetCapable

    @property
    def disablePowerSaving(self):
        """Returns whether the power saving mode can be disabled."""
        return self._disablePowerSaving

    @property
    def dualMode(self):
        """Returns whether the device can run in dual mode."""
        return self._dualMode

    @property
    def wsapiproxy(self):
        """Returns whether the WebSocket API can be used on port 8080."""
        return self._wsapiproxy

    def __repr__(self) -> str:
        return '<Capabilities wsapiproxy=%s, num(caps)=%d>' % (
            self.wsapiproxy, len(self)
        )


class ClockConfig:
    """A class storing the current clock configuration."""

    def __init__(self, root) -> None:
        self._timezoneInfo = _xmlfind_attr(root, 'clockConfig', 'timezoneInfo')
        self._userEnable = _xmlfind_attr(root, 'clockConfig', 'userEnable', default='false') == 'true'
        self._timeFormat = _xmlfind_attr(root, 'clockConfig', 'timeFormat')
        self._userOffsetMinute = int(_xmlfind_attr(root, 'clockConfig', 'userOffsetMinute', default='0'))
        self._brightnessLevel = int(_xmlfind_attr(root, 'clockConfig', 'brightnessLevel', default='0'))
        self._userUtcTime = int(_xmlfind_attr(root, 'clockConfig', 'userUtcTime', default='0'))

    @property
    def timezoneInfo(self):
        """The device's timezone."""
        return self._timezoneInfo

    @property
    def userEnable(self):
        """A value indicating whether the timezone can be altered by a user."""
        return self._userEnable

    @property
    def timeFormat(self):
        """The time format with the following form: `TIME_FORMAT_xxHOUR_ID`."""
        return self._timeFormat

    @property
    def userOffsetMinute(self):
        """The offset in relation to the utc time."""
        return self._userOffsetMinute

    @property
    def brightnessLevel(self):
        """Used to dispaly the clock time."""
        return self._brightnessLevel

    @property
    def userUtcTime(self):
        """The current utc time."""
        return self._userUtcTime

    def __repr__(self) -> str:
        return '<ClockConfig format="%s">' % self.timeFormat


class ClockTime:
    """A class containing the clock time."""
    def __init__(self, root: Element) -> None:
        self._utcTime = int(root.get('utcTime', default='0'))
        self._cueMusic = int(root.get('cueMusic', default='0'))
        self._timeFormat = root.get('timeFormat')
        self._brightness = int(root.get('brightness', default='0'))
        self._clockError = int(root.get('clockError', default='0'))
        self._utcSyncTime = int(root.get('utcSyncTime', default='0'))

        self._year = int(_xmlfind_attr(root, 'localTime', 'year', default='0'))
        self._month = int(_xmlfind_attr(root, 'localTime', 'month', default='0'))
        self._dayOfMonth = int(_xmlfind_attr(root, 'localTime', 'dayOfMonth', default='0'))
        self._dayOfWeek =int( _xmlfind_attr(root, 'localTime', 'dayOfWeek', default='0'))
        self._hour = int(_xmlfind_attr(root, 'localTime', 'hour', default='0'))
        self._minute = int(_xmlfind_attr(root, 'localTime', 'minute', default='0'))
        self._second = int(_xmlfind_attr(root, 'localTime', 'second', default='0'))

    @property
    def year(self):
        return self._year

    @property
    def month(self):
        return self._month

    @property
    def dayOfMonth(self):
        return self._dayOfMonth

    @property
    def dayOfWeek(self):
        return self._dayOfWeek

    @property
    def hour(self):
        return self._hour

    @property
    def minute(self):
        return self._minute

    @property
    def second(self):
        return self._second

    @property
    def utcTime(self):
        return self._utcTime

    @property
    def cueMusic(self):
        return self._cueMusic

    @property
    def timeFormat(self):
        return self._timeFormat

    @property
    def brightness(self):
        return self._brightness

    @property
    def clockError(self):
        return self._clockError

    @property
    def utcSyncTime(self):
        return self._utcSyncTime

    def __repr__(self) -> str:
        return '<ClockTime date="%d/%d/%d", time="%d:%d:%d">' % (
        self.dayOfMonth, self.month, self.year, self.hour, self.minute,
        self.second
        )


class DSPMonoStereo:
    def __init__(self, root: Element) -> None:
        self._mono = _xmlfind_attr(root, 'mono', 'enable', default='false') == 'true'

    @property
    def mono(self):
        return self._mono

    def __repr__(self) -> str:
        return '<DSP mono=%s>' % self.mono


class WirelessProfile:
    def __init__(self, root: Element) -> None:
        self._ssid = _xmlfind(root, 'ssid')

    @property
    def ssid(self):
        return self._ssid

    def __repr__(self) -> str:
        return '<WifiProfile ssid="%s">' % self.ssid


class MediaServer:
    def __init__(self, root: Element) -> None:
        self._id = root.get('id')
        self._mac = root.get('mac')
        self._ip = root.get('ip')
        self._manufacturer = root.get('manufacturer')
        self._model_name = root.get('model_name')
        self._friendly_name = root.get('friendly_name')
        self._model_description = root.get('model_description')
        self._location = root.get('location')

    @property
    def serverid(self):
        return self._id

    @property
    def mac(self):
        return self._mac

    @property
    def ip(self):
        return self._ip

    @property
    def manufacturer(self):
        return self._manufacturer

    @property
    def model_name(self):
        return self._model_name

    @property
    def friendly_name(self):
        return self._friendly_name

    @property
    def model_description(self):
        return self._model_description

    @property
    def location(self):
        return self._location

    def __repr__(self) -> str:
        return '<MediaServer ip="%s", mac="%s", name="%s">' % (
        self.ip, self.mac, self.friendly_name
        )


class MediaServerList:
    def __init__(self, root: Element = None) -> None:
        self._servers = []
        if root:
            for server in root.findall('media_server'):
                self.append(MediaServer(server))

    def append(self, value: MediaServer):
        self._servers.append(value)

    def __getitem__(self, key) -> MediaServer:
        return self._servers[key]

    def __iter__(self) -> Iterator:
        return iter(self._servers)

    def __len__(self) -> int:
        return len(self._servers)

    def __repr__(self) -> str:
        return self._servers.__repr__()


class NetInterface:
    def __init__(self, root: Element) -> None:
        self._name = _xmlfind(root, 'name')
        self._mac = _xmlfind(root, 'mac')
        self._running = _xmlfind(root, 'running')
        self._kind = _xmlfind(root, 'kind')
        self._ssid = _xmlfind(root, 'ssid')
        self._rssi = _xmlfind(root, 'rssi')
        self._frequencyKHz = _xmlfind(root, 'frequencyKHz')
        self._bindings = {}

    @property
    def name(self):
        return self._name

    @property
    def mac(self):
        return self._mac

    @property
    def running(self):
        return self._running

    @property
    def kind(self):
        return self._kind

    @property
    def ssid(self):
        return self._ssid

    @property
    def rssi(self):
        return self._rssi

    @property
    def frequencyKHz(self):
        return self._frequencyKHz

    def __getitem__(self, key) -> str:
        return self._bindings[key]

    def __setitem__(self, key, value):
        self._bindings[key] = value

    def __iter__(self):
        return iter(self._bindings)

    def __len__(self) -> int:
        return len(self._bindings)

    def __repr__(self) -> str:
        return '<NetInterface name="%s", bindings=%s>' % (
        self.name, str(self._bindings)
        )


class NetworkStats:
    def __init__(self, root: Element) -> None:
        self._devid = _xmlfind_attr(root, 'device', 'deviceID')
        self._serial = _xmlfind(root, 'deviceSerialNumber')
        self._interfaces = []
        for interface in root.find('interfaces'):
            self._interfaces.append(NetInterface(interface))

    @property
    def deviceid(self):
        return self._devid

    @property
    def serial(self):
        return self._serial

    def __getitem__(self, key) -> NetInterface:
        return self._interfaces[key]

    def __iter__(self) -> Iterator:
        return iter(self._interfaces)

    def __len__(self) -> int:
        return len(self._interfaces)

    def __repr__(self) -> str:
        return self._interfaces.__repr__()


class NetworkInfoInterface:
    def __init__(self, root: Element) -> None:
        self._iftype = root.get('iftype')
        self._name = root.get('name')
        self._ip = root.get('ip')
        self._ssid = root.get('ssid')
        self._frequencyKHz = root.get('frequencyKHz')
        self._state = root.get('state')
        self._signal = root.get('signal')
        self._mode = root.get('mode')

    @property
    def iftype(self):
        return self._iftype

    @property
    def name(self):
        return self._name

    @property
    def ipaddress(self):
        return self._ip

    @property
    def ssid(self):
        return self._ssid

    @property
    def frequencyKHz(self):
        return self._frequencyKHz

    @property
    def state(self):
        return self._state

    @property
    def signal(self):
        return self._signal

    @property
    def mode(self):
        return self._mode

    def __repr__(self) -> str:
        return '<Interface name="%s", state="%s">' % (self.name, self.state)


class NetworkInfo:
    def __init__(self, root: Element = None) -> None:
        self._interfaces = []
        self._wifi_profile_count = root.get('wifiProfileCount')
        if root:
            for interface in root.find('interfaces'):
                self.append(NetworkInfoInterface(interface))

    def append(self, value: NetworkInfoInterface):
        self._interfaces.append(value)

    def __getitem__(self, key) -> NetworkInfoInterface:
        return self._interfaces[key]

    def __iter__(self) -> Iterator:
        return iter(self._interfaces)

    def __len__(self):
        return len(self._interfaces)

    def __repr__(self) -> str:
        return self._interfaces.__repr__()

    @property
    def wifiprofilecount(self):
        return self._wifi_profile_count


class PowerManagement:
    def __init__(self, root: Element) -> None:
        self._state = _xmlfind(root, 'powerState')
        self._battery_capable = _xmlfind(root, 'capable')

    @property
    def state(self):
        return self._state

    @property
    def battery_capable(self):
        return self._battery_capable

    def __repr__(self) -> str:
        return '<PowerManagement state="%s">' % self.state


class SourceItem:
    def __init__(self, root: Element) -> None:
        self._username = root.text
        self._source = root.get('source')
        self._sourceAccount = root.get('sourceAccount')
        self._status = root.get('status')
        self._isLocal = root.get('isLocal')
        self._multiroomallowed = root.get('multiroomallowed')

    @property
    def source(self):
        return self._source

    @property
    def sourceAccount(self):
        return self._sourceAccount

    @property
    def status(self):
        return self._status

    @property
    def isLocal(self):
        return self._isLocal

    @property
    def multiroomallowed(self):
        return self._multiroomallowed

    @property
    def username(self):
        return self._username


class SourceItemList:
    def __init__(self, root: Element = None) -> None:
        self._items = []
        if root:
            for item in root.find('sources'):
                self.append(SourceItem(root=item))

    def append(self, value: SourceItem):
        self._items.append(value)

    def __getitem__(self, key) -> SourceItem:
        if isinstance(key, str):
            for item in self:
                if item.source == key:
                    return item
        else:
            return self._items[key]

    def __iter__(self) -> Iterator:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)


class SystemTimeout:
    def __init__(self, root: Element) -> None:
        self._powersaving_enabled = _xmlfind(root, 'powersaving_enabled', default='false') == 'true'

    @property
    def powersaving(self) -> bool:
        return self.powersaving

    def __repr__(self) -> str:
        return '<SystemTimeout powersaving=%s>' % self.powersaving


class Preset:
    def __init__(self, root: Element) -> None:
        self._name = _xmlfind(root, "itemName")
        self._id = root.get("id")
        self._source = _xmlfind_attr(root, "ContentItem","source")
        self._type = _xmlfind_attr(root, "ContentItem","type")
        self._location = _xmlfind_attr(root, "ContentItem","location")
        self._source_account = _xmlfind_attr(root,"ContentItem","sourceAccount")
        self._is_presetable = _xmlfind_attr(root,"ContentItem","isPresetable") == "true"
        self._xml = tostring(root.find('ContentItem'))

    @property
    def name(self):
        return self._name

    @property
    def itemid(self):
        return self._id

    @property
    def source(self):
        return self._source

    @property
    def itemtype(self):
        return self._type

    @property
    def location(self):
        return self._location

    @property
    def source_account(self):
        return self._source_account

    @property
    def is_presetable(self):
        return self._is_presetable

    @property
    def xml_str(self) -> str:
        return str(self._xml, 'utf-8')

    def __repr__(self) -> str:
        return '<Preset name="%s", type="%s", source="%s">' % (
            self.name, self.itemtype, self.source
        )


class PresetList:
    def __init__(self, root: Element = None) -> None:
        self._presets = []
        if root:
            for preset in root.findall('preset'):
                self.append(Preset(preset))

    def append(self, value: Preset):
        self._presets.append(value)

    def __getitem__(self, key) -> Preset:
        return self._presets[key]

    def __iter__(self) -> Iterator:
        return iter(self._presets)

    def __len__(self) -> int:
        return len(self._presets)

    def __repr__(self) -> str:
        return self._presets.__repr__()
