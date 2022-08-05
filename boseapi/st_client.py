# MIT License
# 
# Copyright (c) 2022 MatrixEditor
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
__doc__ = """
The SoundTouchClient uses the underlying boseapi to communicate with a 
specified BOSE device. Warning: There are lots of functions that can be 
used to interact with the device. IT is recommended to read the docs before
starting to use a client. 
"""

import urllib3

from xml.etree.ElementTree import fromstring, Element
from typing import overload
from . import all as boseapi

class SoundTouchClient:
  """A simple client to interact with the BOSE WebAPI.

  Note: This client is built to communicate with a BOSE device on port 8090,
  the standard WebAPI port. 

  The client uses an urllib3.PoolManager instance to delegate the HTTP-requests.
  Set a custom manager with the manage_traffic() method. 

  Like the BoseWebSocket, this client can be used in two ways: 1. create a 
  client manually or 2. use the client within a _with_ statement. Additionally,
  this class implements a dict-like functionality. So, the loaded configuration
  can be accessed by typing: `config = client[<config_name>]`

  Attributes:
    device: BoseDevice
      The device to interace with. Some configuration data stored here will be
      updated if specific methods were called in this client.
    _errors: str = 'raise'
      Specifies if the client should raise the exceptions returned by the BOSE
      device. Use `ignore` to ignore the errors (They will be given as the 
      response object in a SoundTouchMessage).
    manager: urllib3.PoolManager
      The manager for HTTP requests to the device.
    config_manager:
      A dict to store the loaded configurations.
  """

  def __init__(self, device: boseapi.BoseDevice, errors: str = 'raise') -> None:
    self.device = device
    self.manager = urllib3.PoolManager(headers={'User-Agent': 'BoseApi/0.1.3'})
    self.config_manager = {}
    self._errors = errors in ['ignore', 'IGNORE']

  def get(self, uri: boseapi.SoundTouchUri) -> boseapi.SoundTouchMessage:
    """Makes a GET request to retrieve a stored value.

    Use this method when querying for specific nodes. All standard nodes
    are implemented by this class.

    Arguments:
      uri: SoundTouchUri
        The node where the requested value is stored. DANGER: This request can also have 
        a massive effect on your BOSE device, for instance when calling
        `client.get(boseapi.nodes.resetDefaults)`, it will wipe all data on the device and 
        perform a factory reset.

    Returns: SoundTouchMessage
      An object storing the request uri, optional a payload that has been sent and the response
      as an `xml.etree.ElementTree.Element`.

    Raises:
      ConnectionError:
        When errors should not be ignored on this client, they will raise a Connection 
        error with all information related to that error.

    Example:
    `message = client.get(boseapi.nodes.volume)`
    """
    message = boseapi.SoundTouchMessage(uri)
    if uri and uri.uri_type == boseapi.SoundTouchUriType.OP_TYPE_EVENT:
      return message

    self._request('GET', message)
    return message

  def options(self, uri: boseapi.SoundTouchUri) -> list:
    """Makes an OPTIONS request and returns the list of available HTTP-Methods.
    
    Use this method when testing whether a node can be accessed.

    Arguments:
      uri: SoundTouchUri
        The node where the requested value is stored. 

    Returns: list[str]
      A list storing all available HTTP-Methods.

    Raises:
      ConnectionError:
        When errors should not be ignored on this client, they will raise a Connection 
        error with all information related to that error.

    Example:
    `methods = client.options(boseapi.nodes.volume)`
    """
    message = boseapi.SoundTouchMessage(uri)
    headers = self._request('OPTIONS', message)
    if type(headers) == int: return []
    return headers['Allow'].split(', ')

  def put(self, uri: boseapi.SoundTouchUri, body) -> boseapi.SoundTouchMessage:
    """Makes a POST request to apply a new value for the given node.

    Use this method when setting some configuration related data. All standard operations
    where a POST request is necessary are implemented by this class.

    Arguments:
      uri: SoundTouchUri
        The node where the requested value is stored.

    Returns: SoundTouchMessage
      An object storing the request uri, optional a payload that has been sent and the response
      as an `xml.etree.ElementTree.Element`.

    Raises:
      ConnectionError:
        When errors should not be ignored on this client, they will raise a Connection 
        error with all information related to that error.

    Example:
    `message = client.put(boseapi.nodes.volume, '<volume>0</volume>')`
    """
    if type(body) != str:
      body = body.to_xml()
    message = boseapi.SoundTouchMessage(uri, body)
    self._request('POST', message)
    return message

  def _raise_error(self, element: Element):
    if self._errors or element.tag != 'errors':
      return
    
    error = element.find('error')
    raise ConnectionError('id=%d, name="%s", cause="%s"' % (
      int(error.get('value', -1)),
      error.get('name', 'NONE'), error.text
    ))

  def _request(self, method: str, msg: boseapi.SoundTouchMessage):
    if not method or not msg:
      return 400 # bad request
    
    if msg.uri not in self.device.supportedUrls:
      return 400

    url = 'http://%s:8090/%s' % (self.device.host, msg.uri)
    try:
      if msg.has_message:
        response = self.manager.request(method, url, body=msg.get_message().encode('utf-8'))
      else:
        response = self.manager.request(method, url)
      
      if response.status == 200:
        if response.data:
          msg.set_response(fromstring(response.data))
          self._raise_error(msg.response)
      
      response.close()
      return response.headers
    except Exception as e:
      raise InterruptedError(e)

  def __enter__(self) -> 'SoundTouchClient':
    return self
  
  def __exit__(self, type, value, traceback) -> None:
    pass

  def __getitem__(self, key):
    if repr(key) in self.config_manager:
      return self.config_manager[repr(key)]

  def __setitem__(self, key, value):
    if type(key) != str:
      key = repr(key)
    self.config_manager[key] = value
  
  def __iter__(self):
    return iter(self.config_manager)

  def _refresh_config(self, uri: boseapi.SoundTouchUri, class_type):
    msg = self.get(uri)
    if msg.response is not None:
      self[uri] = class_type(root=msg.response)
      return self[uri]
  
  def _get_property(self, uri: boseapi.SoundTouchUri, class_type, refresh=True):
    if repr(uri) not in self or refresh:
      self._refresh_config(uri, class_type)
    return self[uri]

  def action(self, key_name: boseapi.keys):
    """Tries to imitate a pressed key.

    This method can be used to invoke different actions by using the different
    keys defined in `boseapi.common.keys`.
    
    Arguments:
      key_name: keys
        The specified key to press.
    """
    temp = f'<key state="%s" sender="Gabbo">{key_name.value}</key>'
    self.put(boseapi.nodes.key, temp % 'press')
    self.put(boseapi.nodes.key, temp % 'release')

  def manage_traffic(self, manager: urllib3.PoolManager):
    """Sets the request manager for this client."""
    if manager: self.manager = manager

###############################################################################
# API functions | set
###############################################################################

  def set_volume(self, level: int) -> boseapi.SoundTouchMessage:
    """Sets the volume to the given level."""
    return self.put(boseapi.nodes.volume, boseapi.cfg.Volume.body(level))
  
  def set_name(self, name: str) -> boseapi.SoundTouchMessage:
    """Sets a new device name."""
    self.device.device_name = name
    return self.put(boseapi.nodes.name, boseapi.cfg.SimpleConfig.body('name', name))

  def select_preset(self, preset: boseapi.cfg.Preset) -> boseapi.SoundTouchMessage:
    """Selects the given preset."""
    if not preset: return
    return self.put(boseapi.nodes.select, preset.xml_str)

  def select_content_item(self, item: boseapi.cfg.ContentItem) -> boseapi.SoundTouchMessage:
    """Selects the given ContentItem."""
    return self.put(boseapi.nodes.select, item.xml_str)

  @overload
  def select_source(self, src: str) -> boseapi.SoundTouchMessage: ...

  def select_source(self, src: boseapi.source) -> boseapi.SoundTouchMessage:
    """Selects a new input source."""
    if not src: return
    return self.select_content_item(boseapi.cfg.ContentItem(src if type(src) == str else src.value))

  def dev_create_zone(self, master: boseapi.BoseDevice, slaves: list) -> boseapi.cfg.Zone:
    """Creates a new multiroom zone with the given devices."""
    if not slaves or len(slaves) == 0: return
    zone = boseapi.cfg.Zone(device_id=master.device_id, ip=master.host, slaves=[
      boseapi.cfg.ZoneSlave(ip_address=x.host, device_id=x.device_id) for x in slaves
    ])
    self.create_zone(zone)
    return zone

  def create_zone(self, zone: boseapi.cfg.Zone) -> boseapi.SoundTouchMessage:
    """Creates a multiroom zone."""
    return self.put(boseapi.nodes.setZone, zone.to_xml())

  def add_zone_slave(self, slaves: list) -> boseapi.SoundTouchMessage: # list[ZoneSlave]
    """Adds the given zone slaves to the device's zone."""
    if not self.zone_status(refresh=True): 
      return
    if not slaves or len(slaves) == 0: 
      return 
    zone = boseapi.cfg.Zone(self.device.device_id, self.device.host, slaves)
    return self.put(boseapi.nodes.addZoneSlave, zone.to_xml())

  def remove_zone_slave(self, slaves: list) -> boseapi.SoundTouchMessage:
    """Removes the given zone slaves from the device's zone."""
    if not self.zone_status(refresh=True): 
      return
    if not slaves or len(slaves) == 0: 
      return 
    zone = boseapi.cfg.Zone(self.device.device_id, self.device.host, slaves)
    return self.put(boseapi.nodes.removeZoneSlave, zone.to_xml())

  def play(self, item: boseapi.cfg.ContentItem) -> boseapi.SoundTouchMessage:
    """Plays the given ContentItem."""
    return self.select_content_item(item)

  def set_bass(self, level: int) -> boseapi.SoundTouchMessage:
    """Sets the device's bass to the given value."""
    return self.put(boseapi.nodes.bass, boseapi.cfg.Bass.body(level))

###############################################################################
# API functions | pre-defined actions
###############################################################################

  def mute(self):
    """Mute the device."""
    self.action(boseapi.keys.MUTE)
  
  def volume_up(self):
    """Higher the volume of the BOSE device by one."""
    self.action(boseapi.keys.VOLUME_UP)
  
  def volume_down(self):
    """Lower the volume of the BOSE device by one."""
    self.action(boseapi.keys.VOLUME_DOWN)
  
  def pause(self):
    """Pause the current media playing."""
    self.action(boseapi.keys.PAUSE)

  def resume(self):
    """Resume the current media playing."""
    self.action(boseapi.keys.PLAY)

  def power(self):
    """Set power on/off."""
    self.action(boseapi.keys.POWER)

###############################################################################
# API functions | properties
###############################################################################

  def volume(self, refresh=True) -> boseapi.cfg.Volume:
    """Queries the current volume config.

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: Volume
      A volume object storing the actual and target volume.
    """
    return self._get_property(boseapi.nodes.volume, boseapi.cfg.Volume, refresh)
  
  def status(self, refresh=True) -> boseapi.cfg.Status:
    """Queries the current playing status.

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: Status
      A status object storing the current media source, ContentItem, track,
      artist, album, preview image, duration, position, play status, shuffle and 
      repeat setting, stream type, track ID, station description and the location
      of the station.
    """
    return self._get_property(boseapi.nodes.nowPlaying, boseapi.cfg.Status, refresh)

  def zone_status(self, refresh=True) -> boseapi.cfg.Zone:
    """Queries the current multiroom config.

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: Zone
      A zone object storing the master ip and device ID as well as the configured
      slaves as a list of ZoneSlaves.
    """
    return self._get_property(boseapi.nodes.getZone, boseapi.cfg.Zone, refresh)
  
  def name(self, refresh=True) -> boseapi.cfg.SimpleConfig:
    """Queries the current name and updates the device's name if possible.

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: SimpleConfig
      A config object storing the queried name.
    """
    name = self._get_property(boseapi.nodes.name, boseapi.cfg.SimpleConfig, refresh)
    if name.value != self.device.device_name:
      self.device.device_name = name.value
    return name

  def bass(self, refresh=True) -> boseapi.cfg.Bass:
    """Queries the current bass config.

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: Bass
      A bass object storing the actual and target bass.
    """
    return self._get_property(boseapi.nodes.bass, boseapi.cfg.Bass, refresh)
  
  def bass_capabilities(self, refresh=True) -> boseapi.cfg.BassCapabilities:
    """Queries the bass capabilities.

    The returned object contains an attribute that states whether these
    capabilities are available on the target device.

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: BassCapabilities:
      An object storing whether bass capabilities are available on the target 
      device.
    """
    return self._get_property(boseapi.nodes.bassCapabilities, boseapi.cfg.BassCapabilities, refresh)

  def balance(self, refresh=True) -> boseapi.cfg.Balance:
    """Queries the current balance config.

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: Balance
      A balance object storing whether it is available to be controlled, its min, 
      max and default value plus the target and actual balance value. 
    """
    return self._get_property(boseapi.nodes.balance, boseapi.cfg.Balance, refresh)

  def capabilities(self, refresh=True) -> boseapi.cfg.Capabilities:
    """Queries the device's capabilities.

    Note: The returned object has a dict-like implementation and individual capabilities
    can be accessed by typing: `capabilities['cap_name']`.

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: Capabilities
      A capabilities object storing a NetworkConfig object (read docs for information),
      some hardware capabilities and additional API capabilities (access through dict).
    """
    return self._get_property(boseapi.nodes.capabilities, boseapi.cfg.Capabilities, refresh)

  def clock_config(self, refresh=True) -> boseapi.cfg.ClockConfig:
    """Queries the current clock config.

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: ClockConfig
      An object storing the timezone info, if it can be enabled by a user, time format,
      offset minute, brightness level and the utc time value. 
    """
    return self._get_property(boseapi.nodes.clockDisplay, boseapi.cfg.ClockConfig, refresh)
  
  def clock_time(self, refresh=True) -> boseapi.cfg.ClockTime:
    """Queries the current clock time.

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: ClockConfig
      An object storing the current time in xml format. See the docs for ClockConfig
      for more information about what values are stored. 
    """
    return self._get_property(boseapi.nodes.clockTime, boseapi.cfg.ClockTime, refresh)

  def dsp_mono(self, refresh=True) -> boseapi.cfg.DSPMonoStereo:
    """Queries the current config for the digital signal processor.

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: DSPMonoStereo
      An object storing a value that indicates whether mono is enabled.
    """
    return self._get_property(boseapi.nodes.DSPMonoStereo, boseapi.cfg.DSPMonoStereo, refresh)
  
  def wifi_profile(self, refresh=True) -> boseapi.cfg.WirelessProfile:
    """Queries the active wireless profile.

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: WirelessProfile
      An object storing the ssid of the active wifi profile.
    """
    return self._get_property(boseapi.nodes.getActiveWirelessProfile, boseapi.cfg.WirelessProfile, refresh)
  
  def language(self, refresh=True) -> boseapi.cfg.SimpleConfig:
    """Queries the current language.

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: SimpleConfig
      An object storing the system language identifier (usually a number).
    """
    return self._get_property(boseapi.nodes.language, boseapi.cfg.SimpleConfig, refresh)
  
  def media_servers(self, refresh=True) -> boseapi.cfg.MediaServerList:
    """Queries all UPnP Media servers found by the BOSE device.

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: MediaServerList
      See MediaServerList documentation for information about how to use this list
      object.
    """
    return self._get_property(boseapi.nodes.listMediaServers, boseapi.cfg.MediaServerList, refresh)

  def net_stats(self, refresh=True) -> boseapi.cfg.NetworkStats:
    """Queries the current network stats.

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: NetworkStats
      See NetworkStats documentation for information about how to use this list
      object.
    """
    return self._get_property(boseapi.nodes.netStats, boseapi.cfg.NetworkStats, refresh)

  def net_info(self, refresh=True) -> boseapi.cfg.NetworkInfo:
    """Queries the current network info. (all available interfaces)

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: NetworkInfo
      See NetworkInfo documentation for information about how to use this list
      object.
    """
    return self._get_property(boseapi.nodes.networkInfo, boseapi.cfg.NetworkInfo, refresh)

  def power_management(self, refresh=True) -> boseapi.cfg.PowerManagement:
    """Queries the current power management status.

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: PowerManagement
      An object storing the power state in if the battery is capable.
    """
    return self._get_property(boseapi.nodes.powerManagement, boseapi.cfg.PowerManagement, refresh)

  def request_token(self, refresh=True) -> boseapi.cfg.SimpleConfig:
    """Requests a new token generated by the device.

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: SimpleConfig
      An object storing the requested token at `config.attrib['value']`.
    """
    return self._get_property(boseapi.nodes.requestToken, boseapi.cfg.SimpleConfig, refresh)
  
  def systemtimeout(self, refresh=True) -> boseapi.cfg.SystemTimeout:
    """Queries whether power saving is enabled or not.

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: SystemTimeout
      An object storing whether power saving is enabled or not.
    """
    return self._get_property(boseapi.nodes.systemtimeout, boseapi.cfg.SystemTimeout, refresh)
  
  def listpresets(self, refresh=True) -> boseapi.cfg.PresetList:
    """Lists all available presets. 

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: PresetList
      See PresetList documentation for information about how to use this list
      object.
    """
    return self._get_property(boseapi.nodes.presets, boseapi.cfg.PresetList, refresh)

  def listsources(self, refresh=True) -> boseapi.cfg.SourceItemList:
    """Lists all available sources. 

    Arguments:
      refresh: bool = True
        If true, the internal configuration object will be replaced by the result
        of this action.
    
    Returns: SourceItemList
      See SourceItemList documentation for information about how to use this list
      object.
    """
    return self._get_property(boseapi.nodes.sources, boseapi.cfg.SourceItemList, refresh)
