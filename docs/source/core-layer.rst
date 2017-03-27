
.. include:: global.rst

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
    :members:
.. autoclass:: Cache
    :members:


DatabaseLayer
------------------
.. module:: bfly.CoreLayer.DatabaseLayer
.. automodule:: DatabaseLayer

You can import ``DatabaseLayer`` from :mod:`bfly` and :mod:`CoreLayer`.


DatabaseLayer classes
************************* 
.. autoclass:: Unqlite
    :members:

:h:`Base class`

.. autoclass:: Database
    :members:

.. _installed: https://github.com/Rhoana/butterfly#butterfly-installation


