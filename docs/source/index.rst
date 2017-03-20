.. butterfly documentation master file, created by
   sphinx-quickstart on Fri Mar 17 13:11:45 2017.


bfly
=======================
.. automodule:: bfly

definitions
-------------

- We refer to system paths relative to ``./``. The path ``./`` gives the root folder of the butterfly source. You can see this path with these commands in a bash shell.

.. code-block:: bash
    
    git clone https://github.com/Rhoana/butterfly
    cd butterfly && pwd

- We call folders or files in the :mod:`bfly` package "layers".
    - You can import them like ``from bfly import CoreLayer``,
    - Or, import from them like ``from bfly.CoreLayer import *``,

All layers
----------------

You can ``import`` bfly from ``./`` or with ``bfly`` installed_.

You can ``from bfly import`` any layer.

.. code-block:: python

    import bfly
    from bfly import DatabaseLayer, AccessLayer
    from bfly import QueryLayer, ImageLayer, UtilityLayer

:ref:`All CoreLayer <The CoreLayer>`
***************************************************
.. autoclass:: CoreLayer
.. autoclass:: DatabaseLayer
.. autoclass:: AccessLayer

:ref:`All QueryLayer <The AccessLayer>`
***************************************************
.. autoclass:: QueryLayer
.. autoclass:: ImageLayer
.. autoclass:: UtilityLayer


The bfly classes
------------------

.. autoclass:: Butterfly
.. autoclass:: Webserver



The CoreLayer
=======================

You can import from ``./`` or with :mod:`bfly` installed_.

.. code-block:: python

    from bfly import CoreLayer

Or, in scripts in some directories:

.. code-block:: python

    # if './bfly/' in sys.path
    import CoreLayer

You can ``from CoreLayer import`` :ref:`all layers`.

.. code-block:: python

    # if './bfly/' in sys.path
    from CoreLayer import DatabaseLayer, AccessLayer
    from CoreLayer import QueryLayer, ImageLayer, UtilityLayer

CoreLayer
-----------------------
.. module:: bfly.CoreLayer
.. automodule:: CoreLayer

You can import ``CoreLayer`` from :mod:`bfly`.


CoreLayer classes
************************* 
.. autoclass:: Core
.. autoclass:: Cache


DatabaseLayer
------------------
.. module:: bfly.CoreLayer.DatabaseLayer
.. automodule:: DatabaseLayer

You can import ``DatabaseLayer`` from :mod:`bfly` and :mod:`CoreLayer`.


DatabaseLayer classes
************************* 
.. autoclass:: Unqlite



The AccessLayer
============================

You can ``import`` from ``./`` or with :mod:`bfly` installed_.

.. code-block:: python

    from bfly import AccessLayer

Or, in scripts in some directories:

.. code-block:: python

    # if './bfly/' in sys.path
    from CoreLayer import AccessLayer
    # if './bfly/CoreLayer/' in sys.path 
    import AccessLayer

You can ``from AccessLayer import`` :ref:`all QueryLayer`.

.. code-block:: python

    # if './bfly/CoreLayer' in sys.path
    from AccessLayer import QueryLayer, ImageLayer, UtilityLayer

AccessLayer
------------------
.. module:: bfly.CoreLayer.AccessLayer
.. automodule:: AccessLayer

You can import ``AccessLayer`` from :mod:`bfly` and :mod:`CoreLayer`.


AccessLayer classes
************************* 
.. autoclass:: API

The QueryLayer
============================

You can ``import`` from ``./`` or with :mod:`bfly` installed_.

.. code-block:: python

    from bfly import QueryLayer

Or, in scripts in some directories:

.. code-block:: python

    # if './bfly/' in sys.path
    from CoreLayer.AccessLayer import QueryLayer
    # if './bfly/CoreLayer/' in sys.path 
    from AccessLayer import QueryLayer
    # if './bfly/CoreLayer/AccessLayer' in sys.path 
    import QueryLayer

You can ``from QueryLayer import`` both :mod:`ImageLayer` and :mod:`UtilityLayer`.

.. code-block:: python

    # if './bfly/CoreLayer/AccessLayer' in sys.path
    from QueryLayer import ImageLayer, UtilityLayer

QueryLayer
----------------------------
.. module:: bfly.CoreLayer.AccessLayer.QueryLayer
.. automodule:: QueryLayer

You can import ``QueryLayer`` from :mod:`bfly`, :mod:`CoreLayer`, and :mod:`AccessLayer`.


QueryLayer classes
************************* 
.. autoclass:: DataQuery
.. autoclass:: TileQuery


ImageLayer
------------------
.. module:: bfly.CoreLayer.AccessLayer.QueryLayer.ImageLayer
.. automodule:: ImageLayer

You can import ``ImageLayer`` from :mod:`bfly`, :mod:`CoreLayer`, :mod:`AccessLayer`, and :mod:`QueryLayer`.


ImageLayer classes
************************* 
.. autoclass:: HDF5


UtilityLayer
------------------
.. module:: bfly.CoreLayer.AccessLayer.QueryLayer.UtilityLayer
.. automodule:: UtilityLayer

You can import ``UtilityLayer`` from :mod:`bfly`, :mod:`CoreLayer`, :mod:`AccessLayer`, and :mod:`QueryLayer`.


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
