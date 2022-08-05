.. _message:

SoundTouch Messages
===================

.. automodule:: boseapi.common.message

The API makes use of an object oriented caller model where Uri-objects are used 
to specify a specific path and action on the device. 

.. contents:: Table of Contents

Interface Functions
-------------------

.. autofunction:: boseapi.common.message.soundtouchuri

Classes
-------

SoundTouchUri
~~~~~~~~~~~~~

.. autoclass:: boseapi.common.message.SoundTouchUri

Some usage examples and behaviour of an SoundTouchUri object.

.. code:: python

  from boseapi.all import nodes, SoundTouchUri

  # Example for the 'volume' node:
  uri = SoundTouchUri("volume")
  
  # len()
  assert len(uri) != 0

  # iterating over each character
  for char in uri:
    print(char)
  
  # compare to another uri
  assert uri == nodes.volume

SoundTouchMessage
~~~~~~~~~~~~~~~~~
.. autoclass:: boseapi.common.message.SoundTouchMessage
  :members:

A simple example of how to use an SoundTouchMessage object follows. It is 
recommended that this class should only be used internally by the client
object.

.. code:: python

  import boseapi.all as boseapi

  # simple message instance
  message = boseapi.SoundTouchMessage(boseapi.nodes.volume)
  device = boseapi.new_device('127.0.0.1')

  with boseapi.SoundTouchClient(device, errors='ignore') as client:
    # This call writes the response object into the message object
    # and returns the response headers on success, 400 otherwise.
    assert type(client._request('GET', message)) != int
    volume = boseapi.cfg.Volume(message.response)

  # The code above is equal to:
  with boseapi.SoundTouchClient(device, errors='ignore') as client:
    volume = client.volume()

nodes
~~~~~~~~~~~~~
.. autoclass:: boseapi.common.message.nodes


Enums
-----

SoundTouchUriScope
~~~~~~~~~~~~~~~~~~

.. autoclass:: boseapi.common.message.SoundTouchUriScope

  .. autoattribute:: OP_SCOPE_PUBLIC
  .. autoattribute:: OP_SCOPE_PRIVATE

SoundTouchUriType
~~~~~~~~~~~~~~~~~

.. autoclass:: boseapi.common.message.SoundTouchUriType
  
  .. autoattribute:: OP_TYPE_EVENT
  .. autoattribute:: OP_TYPE_REQUEST

keys
~~~~

.. autoclass:: boseapi.common.message.keys

Some keys in action:

.. code:: python

  from boseapi.all import new_device, keys, SoundTouchClient
  
  device = new_device('127.0.0.1')
  with SoundTouchClient(device) as client:
    # mute the device with the action() method
    client.action(keys.MUTE)
    # set the device's power on/off
    client.action(keys.POWER)
    # select the device's preset no. 1
    client.action(keys.PRESET_1)

source
~~~~~~

.. autoclass:: boseapi.common.message.source


