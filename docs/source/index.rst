.. butterfly documentation master file, created by
   sphinx-quickstart on Fri Mar 17 13:11:45 2017.

bfly
=======================
.. automodule:: bfly

From :mod:`bfly` import any submodule alias.

.. autoclass:: Core
.. autoclass:: Database
.. autoclass:: Access
.. autoclass:: Query
.. autoclass:: Image
.. autoclass:: Utility

bfly classes
-------------------- 
.. module:: bfly.Butterfly
.. autoclass:: Butterfly

.. module:: bfly.Webserver
.. autoclass:: Webserver

The model layers
=======================

CoreLayer
------------------
.. module:: CoreLayer

..
    From :mod:CoreLayer import any :mod:DatabaseLayer or :mod:AccessLayer submodule alias.

.. autoclass:: Database
.. autoclass:: Access
.. autoclass:: Query
.. autoclass:: Image
.. autoclass:: Utility

CoreLayer classes
************************* 
.. autoclass:: Core
.. autoclass:: Cache


..
    DatabaseLayer
    ------------------
    .. automodule:: bfly.CoreLayer.DatabaseLayer

    DatabaseLayer classes
    ************************* 
    .. autoclass:: Unqlite


    The interface layers
    ============================

    AccessLayer
    ------------------
    .. automodule:: bfly.CoreLayer.AccessLayer

    From :mod:`AccessLayer <bfly.CoreLayer.AccessLayer>` import any :mod:`QueryLayer <bfly.CoreLayer.AccessLayer.QueryLayer>` submodule alias.

    .. autoclass:: Query
    .. autoclass:: Image
    .. autoclass:: Utility

    AccessLayer classes
    ************************* 
    .. autoclass:: API


    QueryLayer
    ------------------
    .. automodule:: bfly.CoreLayer.AccessLayer.QueryLayer

    From :mod:`QueryLayer <bfly.CoreLayer.AccessLayer.QueryLayer>` import the :mod:`ImageLayer <bfly.CoreLayer.AccessLayer.QueryLayer.ImageLayer>` or the :mod:`UtilityLayer <bfly.CoreLayer.AccessLayer.QueryLayer.ImageLayer>` submodule alias.

    .. autoclass:: Image
    .. autoclass:: Utility


    QueryLayer classes
    ************************* 
    .. autoclass:: DataQuery
    .. autoclass:: TileQuery


    ImageLayer
    ------------------
    .. automodule:: bfly.CoreLayer.AccessLayer.QueryLayer.ImageLayer

    ImageLayer classes
    ************************* 
    .. autoclass:: HDF5


    UtilityLayer
    ------------------
    .. automodule:: bfly.CoreLayer.AccessLayer.QueryLayer.UtilityLayer

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

