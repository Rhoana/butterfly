
.. include:: global.rst

The UtilityLayer
============================

You can ``import`` from ``./`` or with :mod:`bfly` installed_.

.. code-block:: python

    from bfly import UtilityLayer

Or, in scripts in some directories:

.. code-block:: python

    # if './bfly/' in sys.path
    from CoreLayer.AccessLayer import UtilityLayer
    # if './bfly/CoreLayer/' in sys.path 
    from AccessLayer import UtilityLayer
    # if './bfly/CoreLayer/AccessLayer' in sys.path 
    from QueryLayer import UtilityLayer
    # if './bfly/CoreLayer/AccessLayer/QueryLayer' in sys.path 
    import UtilityLayer


UtilityLayer
------------------
.. module:: bfly.CoreLayer.AccessLayer.QueryLayer.UtilityLayer
.. automodule:: UtilityLayer

.. autodata:: PORT
.. autodata:: DB_TYPE
.. autodata:: DB_PATH

You can import ``UtilityLayer`` from :mod:`bfly`, :mod:`CoreLayer`, :mod:`AccessLayer`, and :mod:`QueryLayer`.

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

Private classes
*******************
.. autoclass:: NamedStruct
    :members:
.. autoclass:: NamelessStruct
    :special-members:
    :members:

UtilityLayer functions
*************************
.. autofunction:: to_argv

The Settings module
**************************
.. automodule:: UtilityLayer.Settings

The rh_config module
**************************
.. automodule:: UtilityLayer.rh_config

.. _installed: https://github.com/Rhoana/butterfly#butterfly-installation
