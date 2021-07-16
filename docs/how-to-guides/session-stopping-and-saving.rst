.. _stopping_and_saving:

Stopping and Saving
===================

If you know you're not going to be actively working on your project, it's good
manners to :ref:`save your work<saving>` and stop the session, so that
you can release the resources you were consuming. You can do this from the Environments
tab on the RenkuLab UI.

Sometimes an environment will get stuck pending launch (e.g. because you requested
GPUs and they are not yet available). In this case you can view the status and
logs to see if there's a useful message. In the case of pending GPUs, you can
safely wait for the resources to become available. However in other cases, more
commonly when you are trying to customize your environment, you might notice an
issue via the logs, and want to stop the launch so that you can fix the problem
and try again. However, for these stuck notebooks it is not yet possible.
You can reach out to us on `discourse <https://renku.discourse.group>`_ in this
case.

.. _saving:

Saving your work
----------------

Sessions are kept running as long as they in use. In the default
RenkuLab configuration, idle sessions are stopped after 24 hours of
inactivity. Furthermore, sessions can crash, for example if you
run a process that eats more memory than you've allocated. Thus, it's best to
save often.

There are two ways to save your work back to RenkuLab from a session
(both available in JupyterLab and RStudio), and behind the scenes both are using ``git``
staging (``add``), ``commit``, and ``push``. You can type these commands directly
into the available terminal interface of your session, or click
some buttons via the git plugins.

When you push your changes back to RenkuLab, the GitLab CI/CD is triggered to build
a new image out of the ``Dockerfile``, which will be available the next time you
start a new environment.

Saving via Terminal
~~~~~~~~~~~~~~~~~~~

In the Terminal interface inside the session, it is easiest to
use a simple ``renku save`` command to commit and push (i.e. save) any of the changes made
in your project. For example, after updating the ``README.md``:

.. code-block:: console

  renku save
  Successfully saved to remote branch master:
          README.md
  OK

You can also add a custom message with the ``-m`` flag.

.. note::

  ``renku save`` will add commit and push any new *or* modified files

If you would like to it manually to have finer control, you need these three steps:

1. ``git add *``
2. ``git commit -m "my short but descriptive message of the changes I made"``
3. ``git push``

If you are new to git, these resources might be useful:

* `git documentation <https://git-scm.com/doc>`_
* `A great interactive cheat-sheet <http://ndpsoftware.com/git-cheatsheet.html>`_
* `An intro to git <https://rogerdudler.github.io/git-guide/>`_

Saving via Git Plugin
~~~~~~~~~~~~~~~~~~~~~

Find the git plugin interface (Jupyterlab: branched-dots icon on lefthand vertical
menu; RStudio: top right box). Add the changed files you want to save to staging,
write a message to commit the changes, and don't forget to hit the icon or button
to push those changes.

.. _autosave:

Autosave in sessions
------------------------------------

When you stop a session, an automatic check looks for any work
that has not been pushed to the remote repository, including untracked and
modified files. If something is found, a new "autosave" branch is created
and pushed to GitLab.

.. note::

  You cannot start a notebook server from these branches but you can
  still see them listed in GitLab. You can easily identify them because
  their name starts with `renku/autosave/`


Restore unsaved work
~~~~~~~~~~~~~~~~~~~~

The next time you start a new session from the same branch/commit
combination, you will be notified and the autosaved data will be automatically
loaded in your session. Please note that nothing will be pushed automatically
to the `master` branch, therefore you won't see any changes in your project's files
in Renku, nor will the :ref:`provenance <provenance>` be updated.

Local branches you created but never pushed to the origin will not be saved.


Discard autosaved content
~~~~~~~~~~~~~~~~~~~~~~~~~

If you don't need the autosaved content, you can easily discard it using the
following commands:

::

    $ git reset --hard origin/<branch-name> # remove commits and modified files
    $ git clean -f -d # remove untracked files

If you are working on the ``master`` branch, the command looks like this:

::

    $ git reset --hard origin/master && git clean -f -d


Push changes regularly
~~~~~~~~~~~~~~~~~~~~~~

The autosave feature is intended to prevent loss of work, but it is not a
replacement for `git`. By using ``renku save`` or making commits in `git`, you
track your changes and ensure that they are visible to others. And although we
are always working to improve robustness, in some situations, autosave can fail.
So the most secure way to keep your work is to commit and push to origin.
