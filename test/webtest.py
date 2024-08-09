import boseapi.all as boseapi

from xml.etree.ElementTree import Element

device = boseapi.new_device('127.0.0.1')
with boseapi.SoundTouchClient(device) as client:
  # mute the device
  client.mute()