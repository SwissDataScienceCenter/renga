.. _documentation:

Contributing to the Documentation
=================================

You have come across some missing or outdated information in the Renku docs? Why
not submit a pull request to fix it. Contributions to the Renku documentation
are highly appreciated!

Building the docs
-----------------

When inside the ``docs`` directory execute the following two steps to build the
docs:

.. code-block:: console

    $ pipenv install --dev
    $ pipenv run make html

After building the docs you can access them by opening
``_build/html/index.html`` in a browser. Note that the the ``pipenv install --dev``
command has to be run only once or after changing dependencies in the ``Pipfile``.

Editing the docs
----------------

Simply editing and rebuilding the documentation works perfectly fine and is
probably the method of choice for smaller changes. For bigger edits it can be
convenient to have live compiling and browser reloading to immediately see
your changes. To enable this mode, make sure you have all the dependencies installed
(``pipenv install --dev``), then run the following two commands from two separate
terminal windows/tabs.

.. code-block:: console

    $ pipenv run rerun --ignore _build 'make html'
    $ pipenv run httpwatcher --root ./_build/html/

A browser tab with your docs updating live every time a documentation file
changes should have opened automatically.

Any images or non-text snippets that you wish to include in the documentation
can be put into the ``docs/_static`` folder. For example, screenshots can go
in the ``docs/_static/images`` folder.

Running documentation tests
---------------------------

Before submitting a pull request with your documentation changes we ask you
to ensure that the documentation builds (`Building the docs`_) and check your
changes for spelling mistakes by running:

.. code-block:: console

    $ pipenv run sphinx-build -nNW -b spelling -d _build/doctrees ./ _build/spelling
