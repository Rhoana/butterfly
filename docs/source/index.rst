.. butterfly documentation master file, created by
   sphinx-quickstart on Fri Mar 17 13:11:45 2017.

.. include:: global.rst

The bfly package
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
    :noindex:
.. autoclass:: DatabaseLayer
    :noindex:
.. autoclass:: AccessLayer
    :noindex:

:ref:`All QueryLayer <The QueryLayer>`
***************************************************
.. autoclass:: QueryLayer
    :noindex:
.. autoclass:: ImageLayer
    :noindex:
.. autoclass:: UtilityLayer
    :noindex:

The bfly classes
------------------

.. autoclass:: Butterfly
    :members:
    :private-members:

    .. attribute:: BFLY_CONFIG
        :annotation: := Dictionary from rh-config

    .. attribute:: INPUT
        :annotation: := UtilityLayer.INPUT instance

    .. attribute:: RUNTIME
        :annotation: := UtilityLayer.RUNTIME instance

    .. attribute:: OUTPUT
        :annotation: := UtilityLayer.OUTPUT instance

.. autoclass:: Webserver

.. _installed: https://github.com/Rhoana/butterfly#butterfly-installation

The bfly commands
------------------
.. automodule:: __main__
.. autofunction:: bfly.__main__.main


