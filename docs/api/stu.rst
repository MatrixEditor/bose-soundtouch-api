.. _stu:

STU Firmware
============

.. automodule:: boseapi.stu

Module Constants
----------------

.. autoattribute:: boseapi.stu.BOSE_ST_INDEX_URL


Module Interfaces
-----------------

.. autofunction:: boseapi.stu.load_index
.. autofunction:: boseapi.stu.load_lookup

Classes
-------

BoseHardware
~~~~~~~~~~~~

.. autoclass:: boseapi.stu.BoseHardware
  
  .. autofunction:: boseapi.stu.BoseHardware.loadxml


BoseRelease
~~~~~~~~~~~~

.. autoclass:: boseapi.stu.BoseRelease
  
  .. autofunction:: boseapi.stu.BoseRelease.get_url
  .. autofunction:: boseapi.stu.BoseRelease.loadxml

BoseProduct
~~~~~~~~~~~

.. autoclass:: boseapi.stu.BoseProduct

  .. autofunction:: boseapi.stu.BoseProduct.loadxml

