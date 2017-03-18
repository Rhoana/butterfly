.. butterfly documentation master file, created by
   sphinx-quickstart on Fri Mar 17 13:11:45 2017.

butterfly
=====================================
.. automodule:: butterfly

From :mod:`butterfly` import any submodule alias.

.. autoclass:: Core
.. autoclass:: Database
.. autoclass:: Access
.. autoclass:: Query
.. autoclass:: Image
.. autoclass:: Utility

butterfly classes
-------------------- 
.. autoclass:: Butterfly
.. autoclass:: Webserver

The logic layers
=======================

CoreLayer
------------------
.. automodule:: butterfly.CoreLayer

From :mod:`CoreLayer <butterfly.CoreLayer>` import any :mod:`DatabaseLayer <butterfly.CoreLayer.DatabaseLayer>` or :mod:`AccessLayer <butterfly.CoreLayer.AccessLayer>` submodule alias.

.. autoclass:: Database
.. autoclass:: Access
.. autoclass:: Query
.. autoclass:: Image
.. autoclass:: Utility

CoreLayer classes
************************* 
.. autoclass:: Core
.. autoclass:: Cache


DatabaseLayer
------------------
.. automodule:: butterfly.CoreLayer.DatabaseLayer

DatabaseLayer classes
************************* 
.. autoclass:: Unqlite


The interface layers
============================

AccessLayer
------------------
.. automodule:: butterfly.CoreLayer.AccessLayer

From :mod:`AccessLayer <butterfly.CoreLayer.AccessLayer>` import any :mod:`QueryLayer <butterfly.CoreLayer.AccessLayer.QueryLayer>` submodule alias.

.. autoclass:: Query
.. autoclass:: Image
.. autoclass:: Utility

AccessLayer classes
************************* 
.. autoclass:: API


QueryLayer
------------------
.. automodule:: butterfly.CoreLayer.AccessLayer.QueryLayer

From :mod:`QueryLayer <butterfly.CoreLayer.AccessLayer.QueryLayer>` import the :mod:`ImageLayer <butterfly.CoreLayer.AccessLayer.QueryLayer.ImageLayer>` or the :mod:`UtilityLayer <butterfly.CoreLayer.AccessLayer.QueryLayer.ImageLayer>` submodule alias.

.. autoclass:: Image
.. autoclass:: Utility


QueryLayer classes
************************* 
.. autoclass:: DataQuery
.. autoclass:: TileQuery


ImageLayer
------------------
.. automodule:: butterfly.CoreLayer.AccessLayer.QueryLayer.ImageLayer

ImageLayer classes
************************* 
.. autoclass:: HDF5


UtilityLayer
------------------
.. automodule:: butterfly.CoreLayer.AccessLayer.QueryLayer.UtilityLayer

UtilityLayer classes
************************* 
.. autoclass:: INPUT
.. autoclass:: RUNTIME
.. autoclass:: OUTPUT
.. autoclass:: MakeLog


Find modules
===============

* Index:
    * :ref:`General Index <genindex>`
    * :ref:`Module Index <modindex>`
* :ref:`Search <search>`

