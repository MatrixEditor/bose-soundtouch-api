.. _device:

Bose Devices
============

.. automodule:: boseapi.common.device

The core of this API is using a container class which stores all important 
information about a BOSE device. This document contains information about 
how a BoseDevice is structured and how a device can be obtained.

Interface Functions
___________________

.. autofunction:: boseapi.common.device.new_device

Classes
_______

BoseDevice
~~~~~~~~~~
.. autoclass:: boseapi.common.device.BoseDevice
  :members:

Usage of a simple BoseDevice:

.. code:: python

  from boseapi.common.device import new_device

  device = new_device('127.0.0.1')
  
  # iterating over device's components
  for component in device:
    print(component.category)
  
  # get the UPnP location
  url = device.get_upnp_url()

BoseDeviceComponent
~~~~~~~~~~~~~~~~~~~
.. autoclass:: boseapi.common.device.BoseDeviceComponent
  :members: