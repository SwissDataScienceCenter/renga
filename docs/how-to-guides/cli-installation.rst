.. _cli_installation:

Command-line Interface Installation
===================================

The Python-based command-line interface (CLI) and the Python API that we call
``renku`` is available for use via RenkuLab sessions and you can
also install it on your local machine. Most available CLI commands are
documented in our `cheatsheet <https://raw.githubusercontent.com/SwissDataScienceCenter/renku/master/docs/_static/cheatsheet/cheatsheet.pdf>`_

Using the CLI on RenkuLab
-------------------------

The ``renku`` command-line interface is already installed if you start a
Session from RenkuLab with a project you created on RenkuLab or
initialized via ``renku init`` in a local repository.

See :ref:`renku_cli_upgrade` for upgrading to the latest version of the CLI for
Sessions.


Local installation with the script manager ``pipx``
---------------------------------------------------

Install and execute Renku in an isolated environment using ``pipx``.
It will guarantee that there are no version conflicts with dependencies
you are using for your work and research.

.. note::

  This is the method of installation in the renku docker images,
  i.e. the default environment you use when you launch a JupyterLab session
  via the renku browser interface.

`Install pipx <https://github.com/pipxproject/pipx#install-pipx>`_
and make sure that the ``$PATH`` is correctly configured.

::

    $ python3 -m pip install --user pipx
    $ pipx ensurepath

Once ``pipx`` is installed use following command to install ``renku``.

::

    $ pipx install renku
    $ which renku
    ~/.local/bin/renku


.. _upgrading_local:

Upgrading
^^^^^^^^^

To upgrade renku to the latest stable version:

::

    $ pipx upgrade renku

To install renku at a specific version:

::

    $ pipx install --force renku==0.10.3

To upgrade to the latest development version:

::

    $ pipx upgrade --pip-args=--pre renku

If you run into dependency problems during the CLI installation,
have a look at the :ref:`cli-troubleshooting`.

``pip``/``pipenv``
------------------

For development or if the above methods do not work for you, Renku can also
be installed with ``pip`` or ``pipenv``:

.. code-block:: console

  pip install --pre renku

If you want to have Renku as a project dependency, you may install it using
``pipenv`` in your project's directory:

.. code-block:: console

  pipenv install --pre renku
  pipenv shell


Installing from source
----------------------

Using ``conda``, we can very easily install renku from source into an isolated
environment.

Bleeding-edge
^^^^^^^^^^^^^

To install the latest bleeding-edge version of Renku and keep it from
polluting your application environment, an easy solution is to place it inside
an  isolated ``conda`` environment. If you don't have ``conda`` already, you
should `install miniconda <https://conda.io/miniconda.html>`__. Once you have
it installed, you can run

.. code-block:: console

  conda create -y -n renku python=3.6
  $(conda env list | grep '^renku\s' | awk '{print $2}')/bin/pip install -e git+https://github.com/SwissDataScienceCenter/renku-python.git#egg=renku
  mkdir -p ~/.renku/bin
  ln -s "$(conda env list | grep '^renku\s' | awk '{print $2}')/bin/renku" ~/.renku/bin/renku

This will create an isolated environment for renku and link the binary to
``.renku/bin`` in your home directory. If you want to use it, you should
add this to your ``PATH``:

.. code-block:: console

  export PATH=~/.renku/bin:$PATH

If you want it to be done automatically for your shell (bash), add it to ``.bashrc``:

.. code-block:: console

  echo "export PATH=~/.renku/bin:$PATH" >> $HOME/.bashrc
  source $HOME/.bashrc

When you want to update the installed version again, simply do

.. code-block:: console

  $(conda env list | grep '^renku\s' | awk '{print $2}')/bin/pip install -e git+https://github.com/SwissDataScienceCenter/renku-python.git#egg=renku


Specific version
^^^^^^^^^^^^^^^^

To install a specific version of renku the procedure is nearly identical
the above, but instead of installing from source you install a version with ``pip``.
For example, after creating the ``conda`` environment as described in the previous
section, you can install `renku v0.3.0` with

.. code-block:: console

  $(conda env list | grep '^renku\s' | awk '{print $2}')/bin/pip install renku==0.3.0


.. note::

    You may get a ``ValueError: unknown locale: UTF-8`` - see `here
    <https://docs.pipenv.org/diagnose/#valueerror-unknown-locale-utf-8>`_ for
    instructions on how to fix it.
