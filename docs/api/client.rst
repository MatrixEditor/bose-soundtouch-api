.. _client:

SoundTouch Client
=================

.. automodule:: boseapi.client

.. contents:: Table of Contents

Interface
~~~~~~~~~

.. autoclass:: SoundTouchClient
  :members:

Usage
~~~~~

Some usage examples and behavior explaination:

.. code:: python 

  from boseapi.all import *

  device = new_device('127.0.0.1')

  # use the client in a 'with'-statement
  with boseapi.SoundTouchClient(device) as client:
    # refresh the volume config
    volume = client.volume()

    # This volume config can be accessed in two ways:
    # 1. use the nodes.volume object
    volume = client[boseapi.nodes.volume]
    # 2. type the uri path
    volume = client['volume']

    # Iterate over all stored configuration objects:
    for config in client:
      # handle them
      print(config)

    # basic functions: mute, pause/resume, volume up/down
    client.mute()
    client.pause()
    client.resume()
    client.volume_up()
    client.volume_down()

    # press defined keys with .action()
    client.action(Key.MUTE)

    # Play specific media
    item = ContentItem(src=Source.INTERNET_RADIO, location='4712')
    client.play(item)

    # Query and select presets. Returns a PresetList instance.
    presetList = client.listpresets()
    assert len(presetList) > 0
    client.select_preset(preseList[0])

    # Multiroom functionality
    master = device
    slave1 = new_device('127.0.0.2')
    slave2 = new_device('127.0.0.3')

    zone = client.dev_create_zone(master, [slave1, slave2])
    # Add and Remove actions:
    client.add_zone_slave([slave2])
    client.remve_zone_slave([slave1])

    # select different sources
    client.select_source(boseapi.source.BLUETOOTH)



