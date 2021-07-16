.. _troubleshooting:

Troubleshooting
===============

.. _cli-troubleshooting:

CLI installation problems
-------------------------

``psutil`` failure during renku CLI execution or installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using ``pip`` or ``pipx`` can result in a failure of the ``psutil`` dependency
to install correctly. For example:

.. code-block:: shell

  pipx install renku
  ...
  /root/.local/pipx/venvs/renku/include/site/python3.7/psutil" failed with error code 1 in /tmp/pip-install-c7z7y8vs/psutil/
  '/root/.local/pipx/venvs/renku/bin/python -m pip install renku -q' failed

This can be solved in \*nix systems by installing the ``musl`` library. For
example, on Ubuntu:

.. code-block:: shell

  # install the musl library and headers
  apt-get install musl-dev
  # link the library
  ln -s /usr/lib/x86_64-linux-musl/libc.so /lib/libc.musl-x86_64.so.1
