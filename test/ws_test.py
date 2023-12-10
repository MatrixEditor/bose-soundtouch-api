from time import sleep
import boseapi.all as boseapi

# Create a websocket connection only usable together with a device:
device = boseapi.BoseDevice('192.168.189.32')

# 1. Create a websocket by using the 'with' statement:
with boseapi.BoseWebSocket(device) as ws_client:
  # for instance, a simple listener could be added. The listener has
  # to be a function or labda instance that can be called
  ws_client.add_listener('volumeUpdated', None)
  while True: sleep(4)

# 2. Using the websocket with start and stop notification methods:
ws_client = boseapi.BoseWebSocket(device)
ws_client.add_listener('volumeUpdated', None)
ws_client.start_notification()