.. butterfly documentation master file, created by
   sphinx-quickstart on Fri Mar 17 13:11:45 2017.

definitions
=============

- We refer to system paths relative to ``./``. The path ``./`` gives the root folder of the butterfly source. You can see this path with these commands in a bash shell.

.. code-block:: bash
    
    git clone https://github.com/Rhoana/butterfly
    cd butterfly && pwd

- We call folders or files in the :mod:`bfly` package "layers".
    - You can import them like ``from bfly import CoreLayer``,
    - Or, import from them like ``from bfly.CoreLayer import *``,


bfly
=======================
.. automodule:: bfly

You can ``import`` bfly from ``./`` or with :mod:`bfly` installed_.

.. code-block:: python

    import bfly


bfly alias
----------------

You can ``from bfly import`` any layer.

:ref:`All bfly layers <The bfly layers>`
***************************************************
.. autoclass:: Butterfly
.. autoclass:: Webserver
.. autoclass:: CoreLayer

:ref:`All core layers <The core layers>`
***************************************************
.. autoclass:: DatabaseLayer
.. autoclass:: AccessLayer

:ref:`All access layers <The access layers>`
***************************************************
.. autoclass:: QueryLayer
.. autoclass:: ImageLayer
.. autoclass:: UtilityLayer



The bfly layers
=======================

Import all bfly layers from ``./`` or with :mod:`bfly` installed_.

.. code-block:: python

    from bfly import Butterfly, Webserver, CoreLayer

Or, in scripts in some directories:

.. code-block:: python

    # if './bfly/' in sys.path
    import Butterfly, Webserver, CoreLayer


Butterfly
------------
.. module:: bfly.Butterfly
.. automodule:: Butterfly

Butterfly classes
******************
.. autoclass:: Butterfly


Webserver
------------
.. module:: bfly.Webserver
.. automodule:: Webserver

Webserver classes
******************
.. autoclass:: Webserver


CoreLayer
------------------
.. automodule:: bfly.CoreLayer
.. automodule:: CoreLayer

CoreLayer alias
****************
.. autoclass:: DatabaseLayer
.. autoclass:: AccessLayer
.. autoclass:: QueryLayer
.. autoclass:: ImageLayer
.. autoclass:: UtilityLayer

CoreLayer classes
************************* 
.. autoclass:: Core
.. autoclass:: Cache



The core layers
=======================

You can ``import`` all core layers from ``./`` or with :mod:`bfly` installed_.

.. code-block:: python

    from bfly.CoreLayer import DatabaseLayer, AccessLayer

Or, in scripts in some directories:

.. code-block:: python

    # if './bfly/' in sys.path
    from CoreLayer import DatabaseLayer, AccessLayer
    # if './bfly/CoreLayer/' in sys.path 
    import DatabaseLayer, AccessLayer

DatabaseLayer
------------------
.. module:: bfly.CoreLayer.DatabaseLayer
.. module:: CoreLayer.DatabaseLayer
.. automodule:: DatabaseLayer

DatabaseLayer classes
************************* 
.. autoclass:: Unqlite


AccessLayer
------------------
.. module:: bfly.CoreLayer.AccessLayer
.. module:: CoreLayer.AccessLayer
.. automodule:: AccessLayer

AccessLayer alis
****************

.. autoclass:: QueryLayer
.. autoclass:: ImageLayer
.. autoclass:: UtilityLayer

AccessLayer classes
************************* 
.. autoclass:: API


The access layers
============================

You can ``import`` all core layers from ``./`` or with :mod:`bfly` installed_.


.. code-block:: python

    from bfly.AccessLayer import QueryLayer, ImageLayer, UtilityLayer

Or, in scripts in some directories:

.. code-block:: python

    # if './bfly/' in sys.path
    from CoreLayer.AccessLayer import QueryLayer, ImageLayer, UtilityLayer
    # if './bfly/CoreLayer/' in sys.path 
    from AccessLayer import QueryLayer, ImageLayer, UtilityLayer
    # if './bfly/CoreLayer/AccessLayer' in sys.path 
    import QueryLayer, ImageLayer, UtilityLayer


QueryLayer
------------------
.. module:: bfly.CoreLayer.AccessLayer.QueryLayer
.. module:: CoreLayer.AccessLayer.QueryLayer
.. module:: AccessLayer.QueryLayer
.. automodule:: QueryLayer

QueryLayer alias
****************
From :mod:`QueryLayer` import the :mod:`ImageLayer` or the :mod:`UtilityLayer` submodule alias.

.. autoclass:: ImageLayer
.. autoclass:: UtilityLayer

QueryLayer classes
************************* 
.. autoclass:: DataQuery
.. autoclass:: TileQuery


ImageLayer
------------------
.. module:: bfly.CoreLayer.AccessLayer.QueryLayer.ImageLayer
.. automodule:: ImageLayer

ImageLayer classes
************************* 
.. autoclass:: HDF5


UtilityLayer
------------------
.. module:: bfly.CoreLayer.AccessLayer.QueryLayer.UtilityLayer
.. automodule:: UtilityLayer

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


.. _installed: https://github.com/Rhoana/butterfly#butterfly-installation
