.. boseapi documentation master file, created by
   sphinx-quickstart on Wed Aug  3 07:45:34 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

boseapi's documentation
===================================

.. automodule:: boseapi

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/interface

Features
--------

-  various configuration classes 
-  power on/power off
-  play/pause
-  next/previous track
-  volume setting (mute/set volume/volume up/volume down)
-  bass configuration
-  select different media inputs
-  select preset (bookmark)
-  playback selected music
-  Multi room (zones)
-  Websocket notifications

Usage
-----

Installation
~~~~~~~~~~~~

.. code:: shell

   cd bose-soundtouch-api/ && pip install .

Build the docs:

.. code:: shell

   cd docs/ && pip install -U sphinx && sphinx-build -b html source build

Basic Usage
~~~~~~~~~~~

.. code:: python
   
   from boseapi.all import *

   device = new_device('127.0.0.1')
   client = SoundTouchClient(device, errors='ignore')

   # fetch device's capabilities
   capabilities = client.capabilities()
   if capabilities.wsapiproxy:
         # Create and use a WebSocket client
         ws_client = BoseWebSocket(device)
         # Add a listener on an updated volume
         ws_client.add_listener(nodes.volumeupdated, lambda xmlelement: print(xmlelement.tag))
         ws_client.start_notification()

   # Get the current volume and appply a new value to it (0..100).
   volume = client.volume()
   # client.set_volume(7)
   # client.set_volume(volume.actual_vol + 1) 
   # has the same effect as
   client.volume_up()

   # If media is currently played by the device:
   status = client.status()
   if status.play_status != 'PLAY_STATE':
         # Play own media
         item = ContentItem(src=Source.INTERNET_RADIO, location='4712')
         client.play(item)

   # Load and select presets
   presets = client.listpresets()
   if len(presets) > 0:
         preset = presets[0]
         client.select_preset(preset)

   # Multiroom functionality
   current_zone = client.zone_status()
   if current_zone.masterid == None:
         zone = Zone(device_id=device.device_id, ip=device.host)
         
         # Add different zone slaves (it is recommended to create new devices
         # befor adding a zone slave.
         device2 = boseapi.new_device('127.0.0.2')
         slave = ZoneSlave(device_id=device2.device_id, ip_address=device2.host)
         zone.append(slave)

         # Create zone/ Add slaves/ Remove slaves
         client.create_zone(zone)
         client.remove_zone_slave([slave])
         client.add_zone_slave([slave])

   # List all available UPnP MediaServers
   media_servers = client.media_servers()
   if len(media_servers) > 0:
   for server in media_servers:
         print(server)

   # List all available sources
   sources = client.listsources()
   if len(sources) > 0:
   # Get specific source items with the source name
   source_item = sources['QPLAY']
   # or the index position
   source_item2 = sources[0]

   # Select different input sources
   client.select_source(Source.BLUETOOTH)

   if source_item.status == 'READY':
         client.select_source(source_item.source)

   # make sure the node is available be fore fetching data
   if 'GET' in client.options(nodes.bass):
         # manually fetch or set data
         message = client.get(nodes.bass)
         bass = Bass(message.response)
         client.put(nodes.bass, '<bass>0</bass>')



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
