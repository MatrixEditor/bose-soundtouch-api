import websocket

from threading import Thread
from .. import all as boseapi
from xml.etree import ElementTree as xmltree

VOLUME_UPDATE = 'volumeUpdated'
STATUS_UPDATE = 'nowPlayingUpdated'
PRESETS_UPDATE = 'presetsUpdated'
ZONE_UPDATE = 'zoneUpdated'
INFO_UPDATE = 'infoUpdated'
ERROR_HANDLER = 'error'

class WebSocketThread(Thread):
  """
  A small utility class wrapping the WebSocketApp::run_forever() method in an 
  extra Thread.

  Attributes:
    ws: WebSocketApp
      The connection wrapper between this client and the BOSE-device.
  """

  def __init__(self, ws: websocket.WebSocketApp) -> None:
    """
    Arguments:
      ws: WebSocketApp
        A websocket client, that receives notifications from the BOSE device.
    """

    super().__init__()
    self.ws = ws

  def run(self) -> None:
    """Starts the event loop for WebSocket framework."""
    self.ws.run_forever()

class BoseWebSocket:
  """A wrapper class to use the notification system provided by the BOSE devices. 

  In order to react to a message, there is a listener system. You can add
  functions as listener objects. The connection url is defined as follows: 
  'ws://host_ip:8080/'.
  
  The BoseWebSocket can be used in two ways. First, the object can open a 
  connection through start_notification() and secondly, the with-statement
  can be used to create an instance:

  Attributes:
      device: boseapi.BoseDevice
        A BoseDevice instance containing the host ip-address.
      ws_client: websocket.WebSocketApp
        The WebSocketApp containing the WebSocket connection to the
        server.
      chached_listeners: dict[str, Method]
        A dictionary used to store all registered listeners.
  """

  def __init__(self, device:  boseapi.BoseDevice) -> None:
    """
    Arguments:
      device: BoseDevice
        The device instance containing the host ip-address
    """
    self.thread = None
    self.device = device
    self.ws_client = None
    self.cached_listeners = {}

  def start_notification(self):
    """
    Creates, if not already done, a WebSocketThread starts
    the event loop for WebSocket framework.
    """
    if not self.ws_client:
      self.ws_client = websocket.WebSocketApp(
        'ws://%s:8080/' % self.device.host,
        on_message=self._on_packet,
        on_error=self._on_error,
        subprotocols=['gabbo']
      )
      self.thread = WebSocketThread(self.ws_client)
      self.thread.start()

  def stop_notification(self):
    """
    If the connection was successfully established, it can be 
    closed with this function. This method will have no effect when no connection 
    is alive.
    """
    if self.ws_client:
      self.ws_client.close()
      self.ws_client = None

  def __enter__(self) -> 'BoseWebSocket':
    self.start_notification()
    return self

  def __exit__(self, type, value, traceback) -> None:
    self.stop_notification()

  def add_listener(self, category: str, listener) -> bool:
    """Adds a listener provided here to the given category.
    
    Since there are different types of events, the category-string can be used 
    to add a listener to a specific notification category. The listener must take 
    only one argument: xml.etree.ElementTree.Element.

    Arguments:
      category: str 
        The category this listener should be added to.
      listener: Method
        A simple listener method which takes the XML-Element as a passed 
        argument.

    Returns: bool
      True if the listener was added successfully, false otherwise.
    """
    if not category or not listener: return False
    category = repr(category)
    if category in self.cached_listeners:
      self.cached_listeners[category].append(listener)
    else:
      self.cached_listeners[category] = [listener]
    return True

  def remove_listener(self, category: str, listener) -> bool:
    """Removes a listener from the given category.

    Arguments:
      category: str
        The category this listener should be removed from.
      listener: Method
        A simple listener method which takes the XML-Element as a passed 
        argument.
    
    Returns: bool
      True if the listener was removed successfully, false otherwise.
    """
    if not category or not listener: return False
    category = repr(category)
    if category not in self.cached_listeners: return False

    listeners: list = self.cached_listeners[category]
    for ls in listeners:
      if ls == listener:
        listeners.remove(ls)
        return True

  def notify_listeners(self, category, event):
    """Notifies all listeners that ware stored in the given context.

    The name of each context is defined to be the tag element of the update
    XML-Element.

    Arguments:
      category: str
        The category of which listeners should be notified from.
      event: Element
        The event represents an XML-Element with event.tag == category.
    """
    category = repr(category)
    if category in self.cached_listeners:
      for listener in self.get_listener_group(category):
        listener(event)

  def get_listener_group(self, category: str) -> list: # list[function]
    """Searches for a specific category in the registered ones.

    This method is a convenient method to return all listeners that were added
    to a specific context.

    Arguments:
      category: str
        The category name, which has to be one of: VOLUME_UPDATE, STATUS_UPDATE, 
        PRESETS_UPDATE, ZONE_UPDATE, INFO_UPDATE and ERROR_HANDLER
    
    Returns: list[Method]
      A list containing all listeners linked to the given category.
    """
    if not category: return []
    category = repr(category)
    if category not in self.cached_listeners: return []
    return self.cached_listeners[category]

  def _on_packet(self, ws_client, message: bytes):
    root = xmltree.fromstring(message)
    if root.tag == 'updates':
      for update in root[0]:
        self.notify_listeners(update.tag, update)

  def _on_error(self, ws_client, error):
    self.notify_listeners('error', error)
       