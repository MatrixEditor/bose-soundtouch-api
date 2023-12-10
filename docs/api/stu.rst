.. _stu:

STU Firmware
============

.. automodule:: boseapi.firmware

Module Constants
----------------

.. autoattribute:: boseapi.firmware.BOSE_ST_INDEX_URL


Module Interfaces
-----------------

.. autofunction:: boseapi.firmware.load_index
.. autofunction:: boseapi.firmware.load_lookup

Classes
-------

Firmware
~~~~~~~~~~~~

.. autoclass:: boseapi.firmware.Firmware
  
  .. autofunction:: boseapi.firmware.Firmware.loadxml


Release
~~~~~~~~~~~~

.. autoclass:: boseapi.firmware.Release
  
  .. autofunction:: boseapi.firmware.Release.get_url
  .. autofunction:: boseapi.firmware.Release.loadxml

Product
~~~~~~~~~~~

.. autoclass:: boseapi.firmware.Product

  .. autofunction:: boseapi.firmware.Product.loadxml

