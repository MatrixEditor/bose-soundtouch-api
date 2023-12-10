.. _config:

Configuration Structures
========================

.. automodule:: boseapi.model

This document shows all implemented classes that can be obtained through a method
call in a client.

.. contents:: Table of Contents

Classes
-------

Volume
~~~~~~
.. autoclass:: boseapi.model.Volume
  :members:
  
ZoneSlave
~~~~~~~~~
.. autoclass:: boseapi.model.ZoneSlave
  :members:

Zone
~~~~
.. autoclass:: boseapi.model.Zone
  :members:

Example behaviour of a Zone object:

.. code:: python

  from boseapi.model import Zone, ZoneSlave

  zone = Zone(device_id='ID', device_ip='127.0.0.1')
  zone.append(ZoneSlave(device_id='ID2', device_ip='127.0.0.2'))

  # Len()
  assert len(zone) != 0

  # Iterations:
  for slave in zone:
    # act on each slave object
  
  for i in range(len(zone)):
    slave = zone[i]
  
  # Get/Set
  zone[0] = ZoneSlave(device_id='ID3', device_ip='127.0.0.3')
  slave3 = zone[0]


InfoNetworkConfig
~~~~~~~~~~~~~~~~~
.. autoclass:: boseapi.model.InfoNetworkConfig
  :members:

Status
~~~~~~
.. autoclass:: boseapi.model.Status
  :members:

ContentItem
~~~~~~~~~~~
.. autoclass:: boseapi.model.ContentItem
  :members:

SimpleConfig
~~~~~~~~~~~~
.. autoclass:: boseapi.model.SimpleConfig
  :members:

Bass
~~~~
.. autoclass:: boseapi.model.Bass
  :members:

BassCapabilities
~~~~~~~~~~~~~~~~
.. autoclass:: boseapi.model.BassCapabilities
  :members:

Balance
~~~~~~~
.. autoclass:: boseapi.model.Balance
  :members:

Capabilities
~~~~~~~~~~~~
.. autoclass:: boseapi.model.Capabilities
  :members:

.. code:: python

  from boseapi.all import new_device, SoundTouchClient

  device = new_device('127.0.0.1')
  with SoundTouchClient(device) as client:
    capabilities = client.capabilities()
    # iterate over all additional capabilities if len() > 0
    if len(capabilities) > 0:
      for cap_name in capabilities:
        cap_url = capabilites[cap_name]
  
ClockConfig
~~~~~~~~~~~
.. autoclass:: boseapi.model.ClockConfig
  :members:

