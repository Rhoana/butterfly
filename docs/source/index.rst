.. butterfly documentation master file, created by
   sphinx-quickstart on Fri Mar 17 13:11:45 2017.

definitions
=============

- We refer to system paths relative to ``./``. The path ``./`` gives the root folder of the butterfly source. You can see this path with these commands in a bash shell.

.. code-block:: bash
    
    git clone https://github.com/Rhoana/butterfly
    cd butterfly && pwd

- We call subfolders in the ``bfly`` package 'layers'.
    - You can import them like ``from bfly import CoreLayer``,
    - Or, import from them like ``from bfly.CoreLayer import *``,

bfly
=======================
.. automodule:: bfly

.. code-block:: python

    import bfly

bfly alias
----------------

From :mod:`bfly` import any module from any layer.

:ref:`All bfly layers <The bfly layers>`
***************************************************
.. autoclass:: Butterfly
.. autoclass:: Webserver

:ref:`All core layers <The core layers>`
***************************************************
.. autoclass:: CoreLayer
.. autoclass:: DatabaseLayer
.. autoclass:: AccessLayer

:ref:`All access layers <The access layers>`
***************************************************
.. autoclass:: QueryLayer
.. autoclass:: ImageLayer
.. autoclass:: UtilityLayer



The bfly layers
=======================

You can ``import`` all bfly from ``.`` or with ``bfly`` installed.

.. code-block:: python

    from bfly import Butterfly, Webserver, CoreLayer

You can also ``import`` each bfly layer directly from ``./bfly/``.

Butterfly
------------
.. module:: bfly.Butterfly
.. automodule:: Butterfly

.. code-block:: python

    from bfly import Butterfly

Butterfly classes
******************
.. autoclass:: Butterfly

Webserver
------------
.. module:: bfly.Webserver
.. automodule:: Webserver

You can ``import`` the Webserver itself from ``./bfly/``.

.. code-block:: python

    from bfly import Webserver
    import Webserver

Webserver classes
******************
.. autoclass:: Webserver

CoreLayer
------------------
.. automodule:: bfly.CoreLayer
.. automodule:: CoreLayer

You can ``import`` the CoreLayer itself from ``./bfly/``.

.. code-block:: python

    from bfly import CoreLayer
    import CoreLayer

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

Import both core layers as below with bfly or CoreLayer on your ``sys.path``.

.. code-block:: python

    from bfly.CoreLayer import DatabaseLayer, AccessLayer
    from CoreLayer import DatabaseLayer, AccessLayer


DatabaseLayer
------------------
.. module:: bfly.CoreLayer.DatabaseLayer
.. module:: CoreLayer.DatabaseLayer
.. automodule:: DatabaseLayer

.. code-block:: python

    from bfly import DatabaseLayer
    from CoreLayer import DatabaseLayer
    import DatabaseLayer

DatabaseLayer classes
************************* 
.. autoclass:: Unqlite


AccessLayer
------------------
.. module:: bfly.CoreLayer.AccessLayer
.. module:: CoreLayer.AccessLayer
.. automodule:: AccessLayer

.. code-block:: python

    from bfly import AccessLayer
    from CoreLayer import AccessLayer
    import AccessLayer

AccessLayer alis
****************
From :ref:AccessLayer import any :ref:QueryLayer submodule alias.

.. autoclass:: QueryLayer
.. autoclass:: ImageLayer
.. autoclass:: UtilityLayer

AccessLayer classes
************************* 
.. autoclass:: API


The access layers
============================

QueryLayer
------------------
.. module:: bfly.CoreLayer.AccessLayer.QueryLayer
.. module:: CoreLayer.AccessLayer.QueryLayer
.. module:: AccessLayer.QueryLayer
.. automodule:: QueryLayer

.. code-block:: python

    from bfly import QueryLayer
    from CoreLayer import QueryLayer
    from AccessLayer import QueryLayer
    import QueryLayer

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

