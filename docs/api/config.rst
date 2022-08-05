.. _config:

Configuration Structures
========================

.. automodule:: boseapi.common.config

This document shows all implemented classes that can be obtained through a method
call in a client.

.. contents:: Table of Contents

Classes
-------

Volume
~~~~~~
.. autoclass:: boseapi.common.config.Volume
  :members:
  
ZoneSlave
~~~~~~~~~
.. autoclass:: boseapi.common.config.ZoneSlave
  :members:

Zone
~~~~
.. autoclass:: boseapi.common.config.Zone
  :members:

Example behaviour of a Zone object:

.. code:: python

  from boseapi.all.cfg import Zone, ZoneSlave

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
.. autoclass:: boseapi.common.config.InfoNetworkConfig
  :members:

Status
~~~~~~
.. autoclass:: boseapi.common.config.Status
  :members:

ContentItem
~~~~~~~~~~~
.. autoclass:: boseapi.common.config.ContentItem
  :members:

SimpleConfig
~~~~~~~~~~~~
.. autoclass:: boseapi.common.config.SimpleConfig
  :members:

Bass
~~~~
.. autoclass:: boseapi.common.config.Bass
  :members:

BassCapabilities
~~~~~~~~~~~~~~~~
.. autoclass:: boseapi.common.config.BassCapabilities
  :members:

Balance
~~~~~~~
.. autoclass:: boseapi.common.config.Balance
  :members:

Capabilities
~~~~~~~~~~~~
.. autoclass:: boseapi.common.config.Capabilities
  :members:

.. code:: python

  from boseapi.all import new_device, cfg, SoundTouchClient

  device = new_device('127.0.0.1')
  with SoundTouchClient(device) as client:
    capabilities = client.capabilities()
    # iterate over all additional capabilities if len() > 0
    if len(capabilities) > 0:
      for cap_name in capabilities:
        cap_url = capabilites[cap_name]
  
ClockConfig
~~~~~~~~~~~
.. autoclass:: boseapi.common.config.ClockConfig
  :members:

