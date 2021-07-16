.. _session_basics:


Session Basics
==============================

What is a Session?
-----------------------------------

Sessions on RenkuLab are web-based user interfaces (like JupyterLab
and RStudio) that you can launch to develop and run your code and data workflows.
They're commonly used for exploratory analysis because you can try out short blocks
of code before combining everything into a (reproducible) workflow.

You can run JupyterLab or RStudio within a project independently from RenkuLab,
but RenkuLab offers the following advantages:

* Environments hosted in the cloud with a configurable amount of resources
  (memory, CPU, and sometimes GPU).

* Environments are defined using Docker, so they can be shared and reproducibly re-created.

* Auto-saving of work back to RenkuLab, so you can recover when your environment is shut down
  (this happens automatically after 24 hours of inactivity).

* A git client pre-configured with your credentials to easily push your changes
  back to the server.

* The functionality provided by the renku-python_ command-line interface (CLI)
  is automatically available.


What's in my Session?
-------------------------------------

* Your project, which is cloned into the environment on startup.

* Your data files (if the option ``Automatically fetch LFS data`` is selected)
  that are stored in git LFS*.

* All the software required to launch the environment and common tools for
  working with code (``git``, ``git LFS``, ``vim``, etc.).

* Any dependencies you specified via conda (``environment.yml``), using
  language-specific dependency-management facilities (``requirements.txt``,
  ``install.R``, etc.) or installed in the ``Dockerfile``. An exception to
  this is if :ref:`project sets a specific image <renku_ini>`.

* The renku command-line interface renku-python_.

* The amount of CPUs, memory, and (possibly) GPUs that you configured before launch.

For adding or changing software installed into your project's session,
check out :ref:`customizing`


Which Session will launch?
------------------------------------------

The template you choose when you create a project on RenkuLab (or locally call
``renku init`` on your project) determines the kind of session
that is available to launch. Once it is initialized, your project can easily be
modified, for example to install additional libraries into the environment - see
:ref:`customizing`. We provide templates for basic Python, R, and Julia
projects. If you wish to use custom templates for your projects, you can build
your own! Please refer to the :ref:`templating <templates>` documentation.


Starting a new Session
--------------------------------------

When starting a new session, you will be asked to configure it.
The default configuration should work well for most situations. If, however,
you encountered problems with an environment (for example, a crash), you might
want to increase some processing power or memory. Here's the rundown of the
configuration options.

+------------------------------+-------------------------------------------------------------------------------------------+
| Option                       | Description                                                                               |
+==============================+===========================================================================================+
| Branch                       | Default is ``master``. You can switch if you are working on another branch                |
+------------------------------+-------------------------------------------------------------------------------------------+
| Commit                       | Default is the latest, but you can launch the environment from an earlier commit. This is |
|                              | especially useful if your latest commit's build failed (see below) or you have unsaved    |
|                              | work that was automatically recovered.                                                    |
+------------------------------+-------------------------------------------------------------------------------------------+
| Default Image                | This provides information about the Docker image used by the Session.                     |
|                              | When it fails, you can try to rebuild it, or you can check the GitLab job logs.           |
|                              | An image can also be pinned so that new commits will not require a new image              |
|                              | each time.                                                                                |
+------------------------------+-------------------------------------------------------------------------------------------+
| Default environment          | Default is ``/lab``, it loads the JupyterLab interface. If you are working with ``R``,    |
|                              | you may want to use ``/rstudio`` for RStudio. Mind that the corresponding packages need   |
|                              | to be installed in the image. If you're using a python template, the ``rstudio`` endpoint |
|                              | will not work.                                                                            |
+------------------------------+-------------------------------------------------------------------------------------------+
| Number of CPUs               | The number of CPUs available, or the quota. Resources are shared, so please select the    |
|                              | lowest amount that will work for your use case. Usually, the default value works well.    |
+------------------------------+-------------------------------------------------------------------------------------------+
| Amount of Memory             | The amount of RAM available. Resources are shared, so please select the lowest amount     |
|                              | that will work for your use case. Usually, the default value works well.                  |
+------------------------------+-------------------------------------------------------------------------------------------+
| Number of GPUs               | The number of GPUs available. If you can't select any number, no GPUs are available in    |
|                              | RenkuLab deployment you are using. If you request any, you might need to wait for GPUs    |
|                              | to free up in order to be able to launch an environment.                                  |
+------------------------------+-------------------------------------------------------------------------------------------+
| Automatically fetch LFS data | Default is off. All the lfs data will be automatically fetched in if turned on. This is   |
|                              | convenient, but it may considerably slow down the start time if the project contains a    |
|                              | lot of data. Refer to :ref:`Data in Renku <data>` for further information                 |
+------------------------------+-------------------------------------------------------------------------------------------+


What if the Docker image is not available?
------------------------------------------

Sessions are backed by Docker images. When launching a new
session, a container is created from the image that matches the
selected ``branch`` and ``commit``.

A GitLab's CI/CD pipeline automatically builds a new image using the project's
``Dockerfile`` when any of the following happens:

  * Creating of a project.
  * Forking a project (in which the new build happens for the fork).
  * Pushing changes to the project.

The pipeline is defined in the project's :ref:`.gitlab-ci.yml file <gitlab_ci_yml>`. If the
project :ref:`references a specific image <renku_ini>` to use for all environments, the UI
will not check for the image availability - that is usually provided by the project's
maintainer and it doesn't change at every new commit.

It may take a long time to build an image for various reasons, but if you've just created the
project on RenkuLab from one of the templates, it generally takes less than a minute or two.


The Docker image is still building
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the Docker image has a "still building" message, you can either wait patiently,
or watch it build by clicking the associated link to see the streaming log messages
on GitLab. This can be useful if you've made changes to the ``Dockerfile`` or added
lines to ``requirements.txt``, ``environment.yml``, or ``install.R``, where something
might have gone wrong.


The Docker image build failed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If this happens, it's best to click the link to view the logs on GitLab so you
can see what happened. Here are some common reasons for build failure:

Software installation failure
*****************************

**Problem:** You added a new software library to ``requirements.txt``, ``environment.yml``,
or ``install.R``, but something was wrong with the installation (e.g. typo in
the name, extra dependencies required for the library but unavailable).

**How to fix this:**
You can use the GitLab editor or clone your project locally to fix the installation,
possibly by adding the extra dependencies it asks for into the ``Dockerfile``
(the commented out section in the file explains how to do this). As an alternative,
you can start a session from an earlier commit.

**How to avoid this:** First try installing into your running session,
e.g. by running ``pip install -r requirements.txt`` in the terminal on JupyterLab.
You might not have needed to install extra dependencies when installing on your
local machine, but the operating system (OS) defined in the ``Dockerfile`` has
minimal dependencies to keep it lightweight.

The build timed out
*******************

By default, image builds are configured to time out after an hour. If your build
takes longer than that, you might want to check out the section on :ref:`customizing`
sessions before increasing the timeout.

Your project could not be cloned
********************************

If you accidentally added 100s of MBs or GBs of data to your repo and didn't
specify that it should be stored in git LFS, it might take too long to clone. In
this case, read the docs on how to rewrite history and move these files into
git LFS.

Another potential cause is if the project has submodules that are private.

The Docker image is not available
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

RenkuLab uses its internal instance of GitLab to build and store an image in the
registry each time you create a project, push changes, or use the RenkuLab UI to fork
a project. Thus, if you manage to get into a state that skips any of these steps,
the image might be unavailable. It's a workaround, but the easiest way to get out
of this state is to manually trigger a build by adding a new trivial commit through
the GitLab instance, like editing the ``README.md`` file.

.. _renku-python: https://renku-python.readthedocs.org
