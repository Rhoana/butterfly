
.. include:: global.rst

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
    :members:
.. autoclass:: TileQuery
    :members:

:h:`Base class`

.. autoclass:: Query
    :members:

ImageLayer
------------------
.. module:: bfly.CoreLayer.AccessLayer.QueryLayer.ImageLayer
.. automodule:: ImageLayer

You can import ``ImageLayer`` from :mod:`bfly`, :mod:`CoreLayer`, :mod:`AccessLayer`, and :mod:`QueryLayer`.


ImageLayer classes
************************* 
.. autoclass:: HDF5
    :members:

:h:`Base class`

.. autoclass:: Datasource
    :members:


UtilityLayer
------------------
.. module:: bfly.CoreLayer.AccessLayer.QueryLayer.UtilityLayer
.. automodule:: UtilityLayer

You can import ``UtilityLayer`` from :mod:`bfly`, :mod:`CoreLayer`, :mod:`AccessLayer`, and :mod:`QueryLayer`.

UtilityLayer Keywords
***********************
.. autodata:: PORT
.. autodata:: DB_TYPE
.. autodata:: DB_PATH
.. data:: BFLY_CONFIG

UtilityLayer classes
************************* 
.. autoclass:: INPUT
    :members:
.. autoclass:: RUNTIME
    :members:
.. autoclass:: OUTPUT
    :members:
.. autoclass:: MakeLog
    :members:

UtilityLayer functions
*************************
.. autofunction:: to_argv

The Keywords module
**************************
.. automodule:: UtilityLayer.Keywords

The Settings module
**************************
.. automodule:: UtilityLayer.Settings

The rh_config module
**************************
.. automodule:: UtilityLayer.rh_config

Private classes
*******************
.. autoclass:: UtilityLayer.NamedStruct
    :members:
.. autoclass:: UtilityLayer.NamelessStruct
    :members:

.. _installed: https://github.com/Rhoana/butterfly#butterfly-installation
