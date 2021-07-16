.. upgrading_renku:

Upgrading your Renku project
============================

The Renku Project is in constant flux! This means that often there are changes
to RenkuLab (e.g. the web platform (UI) and the knowledge graph (KG)), and the
``renku`` command-line interface (CLI). These docs will explain how to benefit from
changes to the ``renku CLI`` when you're using a session on RenkuLab.
You can find the changes `in the renku-python docs <https://renku-python.readthedocs.io/en/latest/changes.html>`_.

If you're instead looking for a list of new features available in RenkuLab, they
are announced in the :ref:`release_notes`. When we update components of the
RenkuLab platform, you won't usually have to do anything special. E.g. when we
added the ability for anonymous (not logged in) users to launch sessions, 
each project was immediately accessible without the project owner
needing to change any settings.

.. _renku_cli_upgrade:

Upgrading your image to use the latest ``renku`` CLI version
------------------------------------------------------------

.. note::

  This section is for upgrading the version of ``renku`` CLI installed into
  the Sessions on RenkuLab for your project. See :ref:`upgrading_local`
  for upgrading your local machine's version of ``renku``.

When we release a new version of the ``renku`` CLI, you do have to make some
(minimal) changes to the ``Dockerfile`` in your project to ensure that the
Session on RenkuLab will use the image with the correct version.

The version of the ``renku`` CLI is defined in the base image specified in the
``FROM`` line (usually line 1) of the ``Dockerfile`` in your repo.

1. Replace this line with the latest available image for the "flavor" you're using,
   which you can find by:

* checking the `renkulab-docker repo README.md <https://github.com/SwissDataScienceCenter/renkulab-docker/blob/master/README.md>`_
  for the naming conventions of the "flavor" of image you're updating (e.g. if you're using
  the "minimal python project", you will look in the ``py`` section)
* visiting the dockerhub page linked in the naming conventions section in the above ``README``
* choosing the latest available tagged image

Note that the version of the ``renku`` CLI is defined in the image name. For example,
``renku/renkulab-py:3.7-renku0.10.4-0.6.3`` has CLI version ``0.10.4``. Please choose
an image with the renku version specified (e.g. ``-renku0.10.4-`` and not ``-renku-``),
unless you absolutely need the latest development version of ``renku``, since it makes
debugging and reproducibility much simpler.

2. Push your changes (either from the GitLab editor, or in a running Session), 
   and start up a new Session from the latest commit to use this new image.

3. When you start to run ``renku`` commands, you might be asked to call ``renku migrate``.
   This command ensures that the metadata in your project is updated.

Test drive
^^^^^^^^^^

If you just want to try out the latest version of ``renku`` without building a new
image yet, you can follow the ``pipx`` installation instructions from
:ref:`upgrading your local installation <upgrading_local>`. Installing in this way,
like any other terminal install, will not hold through the next time you launch.

Keep in mind that your project's metadata will be upgraded when you start running
the new version ``renku`` commands - don't push these changes if you want to revert
back to an older version.

You should follow the steps in the previous section to swap out the base image
once you're satisfied with latest ``renku``.

Only updating the renku CLI
^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to use the latest version of ``renku`` but for some reason cannot rebuild
from scratch the rest of the docker image layers for your project (e.g. dependency issues),
you can add the ``pipx`` installation from
:ref:`upgrading your local installation <upgrading_local>` to the end of your ``Dockerfile``;
e.g. ``RUN pipx install renku==<VERSION> --force``.

When the gitlab CI builds an image using the ``Dockerfile`` in your project, it
re-uses layers of installs that haven't changed between builds, which speeds up
the build process. But, when you swap out the base image (as is recommended), all
of the subsequent layers might need to rebuild.

We still recommend swapping out the base image when possible.
