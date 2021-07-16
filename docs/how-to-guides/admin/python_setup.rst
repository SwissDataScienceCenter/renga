.. _python_setup:

Python setup
============

**Renku** requires ``python`` 3.6+.


Installation (MacOS users)
--------------------------

This setup assumes you have got ``Homebrew`` installed in your computer. If not
please look `here <https://brew.sh>`_. To check which version of python is
already installed you can use:

.. code-block:: console

    $ python -version

If you have python 2 you can consider removing it with

.. code-block:: console

    $ brew uninstall --force python@2

Before installing Python 3 add the following line to ``~/.profile``

.. code-block:: console

    $ export PATH="/usr/local/opt/python/libexec/bin:$PATH"

and install ``xcode-select``

.. code-block:: console

    $ xcode-select --install

To install Python:

.. code-block:: console

    $ brew install python

To check if Python 3 gets installed correctly do ``python --version`` again.
