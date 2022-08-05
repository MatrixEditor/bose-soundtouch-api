import boseapi.all as boseapi

from xml.etree.ElementTree import Element

device = boseapi.new_device('192.168.189.32')
with boseapi.SoundTouchClient(device) as client:
  # mute the device
  client.mute()