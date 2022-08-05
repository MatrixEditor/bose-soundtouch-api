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
from xml.etree.ElementTree import Element
from enum import Enum

class SoundTouchUriScope(Enum):
  """ A simple EnumWrapper defining the URI scope.

  The chosen URI scopen can be either OP_SCOPE_PUBLIC or OP_SCOPE_PRIVATE.
  """

  OP_SCOPE_PUBLIC = 0x00
  """
  URIs that are public and can be accessed by everyone will be declared
  with OP_SCOPE_PUBLIC.
  """

  OP_SCOPE_PRIVATE = 0x01
  """
  URIs that are private and can not be accessed by everyone.
  """

class SoundTouchUriType(Enum):
  """ A simple EnumWrapper defining the URI type."""
  
  OP_TYPE_EVENT = 0x04
  """
  URIs that are used to capture events can not be queried with a client. 
  Therefore, the BoseWebSocket should be used.
  """

  OP_TYPE_REQUEST = 0x08
  """
  Standard URI type.
  """

class SoundTouchUri:
  """A class barely behaving like a string instance.

  An SoundTouchUri object can be used in several ways. Since, the object can not
  be edited, there is no editing available.

  The __str__ and __repr__ method will return the assigned path name (created when
  initiating a new instance).

  Attributes:
    path: str
      The target uri which will be formatted into the url in a request.
    scope: SoundTouchUriScope
      The scope of this URI object. If it is private, the client may not 
      request the resource.
    uri_type: SoundTouchUriType
      Defines the type of this uri - it can be either 'request' or 'event'.
  """
  def __init__(
    self,
    path: str,
    scope: SoundTouchUriScope = SoundTouchUriScope.OP_SCOPE_PUBLIC,    
    uri_type: SoundTouchUriType = SoundTouchUriType.OP_TYPE_REQUEST
  ) -> None:
    self.path = path
    self.scope = scope
    self.uri_type = uri_type

  def __repr__(self) -> str:
    return self.__str__()
  
  def __str__(self) -> str:
    return self.path
  
  def __eq__(self, __o: object) -> bool:
    return self.path.__eq__(__o)
  
  def __len__(self) -> int:
    return self.path.__len__()
  
  def __getitem__(self, key):
    return self.path[key]
  
class SoundTouchMessage:
  """A class representing an exchange object.

  In order to exchange data between a client and the device, this class
  type is used. It stores the request text/uri and the response as an XML-
  Element.
  
  Attributes:
    uri: SoundTouchUri
      The target uri which should be queried.
    xml_message: str
      If a key should be pressed or new data should be saved on the target
      device, a xml formatted string is needed.
    response: xml.etree.ElementTree.Element
      The response object as an XML-Element.
  """

  def __init__(
    self,
    uri: SoundTouchUri = None,
    xml_message: str = None,
    response: Element = None
  ) -> None:
    self.uri = uri
    self.xml_message = xml_message
    self.response = response

  def __str__(self) -> str:
    return 'SoundTouchMessage{ uri="%s", xml_message=%s, response=%s }' % (
      self.uri.path, self.xml_message is not None, self.is_simple_response()
    )
  
  def get_message(self) -> str: # str | None
    """Returns the xml formatted message string."""
    return self.xml_message
  
  @property
  def has_message(self) -> bool:
    return self.get_message() is not None
  
  def is_simple_response(self) -> bool:
    return self.response and len(self.response) != 0

  def set_response(self, response_object: Element):
    """Set the response object."""
    if type(response_object) == Element:
      self.response = response_object
  
class nodes:
  """
  This class contains all SoundTouchUris that should be implemented by a 
  BOSE device. They were taken from the following files:

  >>> rootfs/opt/Bose/etc/HandCraftedWebServer-SoundTouch.xml
  >>> rootfs/opt/Bose/etc/WebServer-SoundTouch.xml

  """
  AbortSoftwareUpdate              = SoundTouchUri("AbortSoftwareUpdate")
  addGroup                         = SoundTouchUri("addGroup")
  addStation                       = SoundTouchUri("addStation")
  addStereoPair                    = SoundTouchUri("addStereoPair")
  addWirelessProfile               = SoundTouchUri("addWirelessProfile")
  addZoneSlave                     = SoundTouchUri("addZoneSlave")
  art                              = SoundTouchUri("art")
  balance                          = SoundTouchUri("balance") #
  bass                             = SoundTouchUri("bass") #
  bassCapabilities                 = SoundTouchUri("bassCapabilities") # 
  bluetoothInfo                    = SoundTouchUri("bluetoothInfo") 
  bookmark                         = SoundTouchUri("bookmark") 
  cancelPairLightswitch            = SoundTouchUri("cancelPairLightswitch") 
  capabilities                     = SoundTouchUri("capabilities") # 
  clearBluetoothPaired             = SoundTouchUri("clearBluetoothPaired")  
  clearPairedList                  = SoundTouchUri("clearPairedList") 
  clockDisplay                     = SoundTouchUri("clockDisplay") # 
  clockTime                        = SoundTouchUri("clockTime") # 
  criticalError                    = SoundTouchUri("criticalError", SoundTouchUriScope.OP_SCOPE_PRIVATE)
  criticalErrorUpdate              = SoundTouchUri("criticalErrorUpdate", uri_type=SoundTouchUriType.OP_TYPE_EVENT)
  DSPMonoStereo                    = SoundTouchUri("DSPMonoStereo") # 
  enterBluetoothPairing            = SoundTouchUri("enterBluetoothPairing")
  enterPairingMode                 = SoundTouchUri("enterPairingMode")
  errorNotification                = SoundTouchUri("errorNotification", uri_type=SoundTouchUriType.OP_TYPE_EVENT)
  factoryDefault                   = SoundTouchUri("factoryDefault", SoundTouchUriScope.OP_SCOPE_PRIVATE)
  genreStations                    = SoundTouchUri("genreStations")
  getActiveWirelessProfile         = SoundTouchUri("getActiveWirelessProfile")
  getBCOReset                      = SoundTouchUri("getBCOReset")
  getGroup                         = SoundTouchUri("getGroup")
  getZone                          = SoundTouchUri("getZone") # 
  groupUpdated                     = SoundTouchUri("groupUpdated", uri_type=SoundTouchUriType.OP_TYPE_EVENT)
  info                             = SoundTouchUri("info") # 
  introspect                       = SoundTouchUri("introspect")
  key                              = SoundTouchUri("key")
  language                         = SoundTouchUri("language") # 
  languageUpdated                  = SoundTouchUri("languageUpdated", uri_type=SoundTouchUriType.OP_TYPE_EVENT)
  listMediaServers                 = SoundTouchUri("listMediaServers") # 
  lowPowerStandby                  = SoundTouchUri("lowPowerStandby")
  LowPowerStandbyUpdate            = SoundTouchUri("LowPowerStandbyUpdate", SoundTouchUriScope.OP_SCOPE_PRIVATE, SoundTouchUriType.OP_TYPE_EVENT)
  marge                            = SoundTouchUri("marge") # undefined behaviour
  masterMsg                        = SoundTouchUri("masterMsg")
  name                             = SoundTouchUri("name") # 
  nameSource                       = SoundTouchUri("nameSource")
  nameUpdated                      = SoundTouchUri("nameUpdated", uri_type=SoundTouchUriType.OP_TYPE_EVENT)
  navigate                         = SoundTouchUri("navigate")
  netStats                         = SoundTouchUri("netStats") # 
  networkInfo                      = SoundTouchUri("networkInfo") # 
  notification                     = SoundTouchUri("notification")
  nowPlaying                       = SoundTouchUri("nowPlaying") # 
  nowPlayingUpdated                = SoundTouchUri("nowPlayingUpdated", uri_type=SoundTouchUriType.OP_TYPE_EVENT)
  nowSelection                     = SoundTouchUri("nowSelection")
  nowSelectionUpdated              = SoundTouchUri("nowSelectionUpdated", uri_type=SoundTouchUriType.OP_TYPE_EVENT)
  pairLightswitch                  = SoundTouchUri("pairLightswitch")
  pdo                              = SoundTouchUri("pdo")
  performWirelessSiteSurvey        = SoundTouchUri("performWirelessSiteSurvey")
  playbackRequest                  = SoundTouchUri("playbackRequest")
  playNotification                 = SoundTouchUri("playNotification", SoundTouchUriScope.OP_SCOPE_PRIVATE)
  powerManagement                  = SoundTouchUri("powerManagement") # 
  powersaving                      = SoundTouchUri("powersaving")
  presets                          = SoundTouchUri("presets")
  presetsUpdated                   = SoundTouchUri("presetsUpdated", uri_type=SoundTouchUriType.OP_TYPE_EVENT)
  pushCustomerSupportInfoToMarge   = SoundTouchUri("pushCustomerSupportInfoToMarge")
  recents                          = SoundTouchUri("recents")
  recentsUpdated                   = SoundTouchUri("recentsUpdated", uri_type=SoundTouchUriType.OP_TYPE_EVENT)
  removeGroup                      = SoundTouchUri("removeGroup")
  removeMusicServiceAccount        = SoundTouchUri("removeMusicServiceAccount")
  removePreset                     = SoundTouchUri("removePreset")
  removeStation                    = SoundTouchUri("removeStation")
  removeStereoPair                 = SoundTouchUri("removeStereoPair")
  removeZoneSlave                  = SoundTouchUri("removeZoneSlave")
  requestToken                     = SoundTouchUri("requestToken") # 
  search                           = SoundTouchUri("search")
  searchStation                    = SoundTouchUri("searchStation")
  select                           = SoundTouchUri("select")
  selectLastSoundTouchSource       = SoundTouchUri("selectLastSoundTouchSource")
  selectLastSource                 = SoundTouchUri("selectLastSource")
  selectLastWiFiSource             = SoundTouchUri("selectLastWiFiSource")
  selectLocalSource                = SoundTouchUri("selectLocalSource")
  selectPreset                     = SoundTouchUri("selectPreset")
  serviceAvailability              = SoundTouchUri("serviceAvailability")
  services                         = SoundTouchUri("services")
  setBCOReset                      = SoundTouchUri("setBCOReset")
  setComponentSoftwareVersion      = SoundTouchUri("setComponentSoftwareVersion", SoundTouchUriScope.OP_SCOPE_PRIVATE)
  setMargeAccount                  = SoundTouchUri("setMargeAccount")
  setMusicServiceAccount           = SoundTouchUri("setMusicServiceAccount")
  setMusicServiceOAuthAccount      = SoundTouchUri("setMusicServiceOAuthAccount")
  setPairedStatus                  = SoundTouchUri("setPairedStatus")
  setPairingStatus                 = SoundTouchUri("setPairingStatus")
  setPower                         = SoundTouchUri("setPower")
  setProductSerialNumber           = SoundTouchUri("setProductSerialNumber", SoundTouchUriScope.OP_SCOPE_PRIVATE)
  setProductSoftwareVersion        = SoundTouchUri("setProductSoftwareVersion", SoundTouchUriScope.OP_SCOPE_PRIVATE)
  setup                            = SoundTouchUri("setup")
  setWiFiRadio                     = SoundTouchUri("setWiFiRadio", SoundTouchUriScope.OP_SCOPE_PRIVATE)
  setZone                          = SoundTouchUri("setZone")
  slaveMsg                         = SoundTouchUri("slaveMsg")
  SoftwareUpdateExit               = SoundTouchUri("SoftwareUpdateExit")
  soundTouchConfigurationStatus    = SoundTouchUri("soundTouchConfigurationStatus")
  soundTouchConfigurationUpdated   = SoundTouchUri("soundTouchConfigurationUpdated", uri_type=SoundTouchUriType.OP_TYPE_EVENT)
  sourceDiscoveryStatus            = SoundTouchUri("sourceDiscoveryStatus")
  sources                          = SoundTouchUri("sources")
  sourcesUpdated                   = SoundTouchUri("sourcesUpdated", uri_type=SoundTouchUriType.OP_TYPE_EVENT)
  speaker                          = SoundTouchUri("speaker")
  standby                          = SoundTouchUri("standby")
  StartSoftwareUpdate              = SoundTouchUri("StartSoftwareUpdate")
  stationInfo                      = SoundTouchUri("stationInfo")
  storePreset                      = SoundTouchUri("storePreset")
  supportedURLs                    = SoundTouchUri("supportedURLs")
  swUpdateAbort                    = SoundTouchUri("swUpdateAbort")
  swUpdateCheck                    = SoundTouchUri("swUpdateCheck")
  swUpdateQuery                    = SoundTouchUri("swUpdateQuery")
  swUpdateStart                    = SoundTouchUri("swUpdateStart")
  swUpdateStatusUpdated            = SoundTouchUri("swUpdateStatusUpdated", uri_type=SoundTouchUriType.OP_TYPE_EVENT)
  systemtimeout                    = SoundTouchUri("systemtimeout")
  test                             = SoundTouchUri("test")
  testCommandBA                    = SoundTouchUri("testCommandBA", uri_type=SoundTouchUriType.OP_TYPE_EVENT)
  testCommandSU                    = SoundTouchUri("testCommandSU", uri_type=SoundTouchUriType.OP_TYPE_EVENT)
  trackInfo                        = SoundTouchUri("trackInfo")
  updateGroup                      = SoundTouchUri("updateGroup")
  userActivity                     = SoundTouchUri("userActivity", SoundTouchUriScope.OP_SCOPE_PRIVATE)
  userPlayControl                  = SoundTouchUri("userPlayControl")
  userRating                       = SoundTouchUri("userRating")
  userTrackControl                 = SoundTouchUri("userTrackControl")
  volume                           = SoundTouchUri("volume")
  volumeupdated                    = SoundTouchUri("volumeupdated", uri_type=SoundTouchUriType.OP_TYPE_EVENT)
  zoneUpdated                      = SoundTouchUri("zoneUpdated", uri_type=SoundTouchUriType.OP_TYPE_EVENT)
  audiodspcontrols                 = SoundTouchUri("audiodspcontrols")
  audiospeakerattributeandsetting  = SoundTouchUri("audiospeakerattributeandsetting")
  productcechdmicontrol            = SoundTouchUri("productcechdmicontrol")
  producthdmiassignmentcontrols    = SoundTouchUri("producthdmiassignmentcontrols")
  audioproducttonecontrols         = SoundTouchUri("audioproducttonecontrols")
  audioproductlevelcontrols        = SoundTouchUri("audioproductlevelcontrols")
  systemtimeoutcontrol             = SoundTouchUri("systemtimeoutcontrol")
  rebroadcastlatencymode           = SoundTouchUri("rebroadcastlatencymode")

class source(Enum):
  """
  Defines the source of a ContentItem. With client.select_source(), the input 
  source of the current media can be changed.
  """

  DEFAULT = "invalid_source"
  STORED_MUSIC = "stored_music"
  INTERNET_RADIO = "internet_radio"
  SPOTIFY = "spotify"
  PANDORA = "pandora"
  DEEZER = "deezer"
  IHEART = "iheart"
  SIRIUSXM = "siriusxm"
  BLUETOOTH = "bluetooth"
  AUX = "aux"
  AMAZON = "amazon"
  AIRPLAY = "airplay"
  QPLAY = "qplay"
  UPDATE = "update"
  NOTIFICATION = "notification"
  LOCAL_MUSIC = "local_music"
  INVALID = "invalid_source"
  STANDBY = "standby"

class keys(Enum):
  """
  This class contains all usable that can be 'pressed' on a BOSE-device. To
  use a key within an action of  the client, type: client.action(keys.<KEY>)
  """

  PLAY = 'PLAY'
  PAUSE = 'PAUSE'
  PLAY_PAUSE = 'PLAY_PAUSE'
  STOP = 'STOP'
  PREV_TRACK = 'PREV_TRACK'
  NEXT_TRACK = 'NEXT_TRACK'
  THUMBS_UP = 'THUMBS_UP'
  THUMBS_DOWN = 'THUMBS_DOWN'
  BOOKMARK = 'BOOKMARK'
  POWER = 'POWER'
  MUTE = 'MUTE'
  VOLUME_UP = 'VOLUME_UP'
  VOLUME_DOWN = 'VOLUME_DOWN'
  PRESET_1 = 'PRESET_1'
  PRESET_2 = 'PRESET_2'
  PRESET_3 = 'PRESET_3'
  PRESET_4 = 'PRESET_4'
  PRESET_5 = 'PRESET_5'
  PRESET_6 = 'PRESET_6'
  AUX_INPUT = 'AUX_INPUT'
  SHUFFLE_OFF = 'SHUFFLE_OFF'
  SHUFFLE_ON = 'SHUFFLE_ON'
  REPEAT_OFF = 'REPEAT_OFF'
  REPEAT_ONE = 'REPEAT_ONE'
  REPEAT_ALL = 'REPEAT_ALL'
  ADD_FAVORITE = 'ADD_FAVORITE'
  REMOVE_FAVORITE = 'REMOVE_FAVORITE'
 
def soundtouchuri() -> dict: # dict[str, type]
  """
  Returns: dict[str, type]
    A dict with all implemented SoundTouchUris together with their path value.
  """
  ops = vars(nodes)
  copy = {}
  for key in ops:
    if type(ops[key]) == SoundTouchUri:
      copy[key] = ops[key]
  return copy