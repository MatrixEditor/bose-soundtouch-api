.. _ws:

WebSocket Notifications
=======================

This part of the developer documentation covers all classes and usable functions 
of the boseapi.ws module. Use this module if you want to receive notifications 
from a BOSE-device.

BoseWebSocket
-------------

.. automodule:: boseapi.ws

.. autoclass:: BoseWebSocket
  :members:

Usage of a simple BoseWebSocket:

.. code:: python
  
  from boseapi.all import new_device, BoseWebSocket
  
  device = new_device('127.0.0.1')
  socket = BoseWebSocket(device)
  
  # 1. Open a connection and start listening
  socket.start_notification()

  # 2. Use the socket in a `with`-statement:
  with BoseWebSocket(device) as socket:
    # e.g. register some listeners
    # when the `with`-statement closes, the notifications will be stopped

