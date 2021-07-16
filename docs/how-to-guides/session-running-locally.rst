.. _local_sessions:

Running RenkuLab Interactive Sessions on Your Own Machine
=========================================================

Each Renku project contains configuration files (``Dockerfile``,
``requirements.txt`` etc.) for building reproducible session images. We build
these automatically when you push your project to the server and store them in
the image registry connected to the Renku instance that you are using. The
custom-built images are used whenever you launch an interactive session on
RenkuLab.

You can of course also use these same images to run your code in the correct
environment anywhere that `Docker <https://www.docker.com>`_ is available.

.. note::

    All of the instructions below assume that you have cloned your project
    locally and that you have `Docker installed
    <https://docs.docker.com/get-docker/>`_. On Linux systems, Docker requires
    root privileges - if you do not have root access to the host, you might
    consider `rootless Docker
    <https://docs.docker.com/engine/security/rootless/>`_.


Building your own image
-----------------------

If you are working on a project that has not yet been pushed to the server, or
you just prefer to build the image locally, you can certainly do so with Docker.
To build the image, run this command from the root directory of your project:

.. code-block:: console

    $ docker build -t <imageName>:<tag> .

The ``imageName`` and ``tag`` can be anything you want, but you might want to
try to use something you will remember. To see which images you have in your
local Docker registry, run

.. code-block:: console

    $ docker images


Using the images built on RenkuLab
----------------------------------

The easiest way to spin up your runtime environment locally is by pulling the
image that has already been built.

First, make sure that your project has been pushed and that the image build is
complete. If you are not sure, the easiest way to check is to navigate to your
project in RenkuLab and go to launch a new session - if the "Start environment"
button is available, it means the image has been built already.

To pull the image, you need to construct the image name. This is typically the
format to expect:
``registry.<renku-host>/<namespace>/<project>:<commit-sha-7>``. Lets break down
the meaning of these terms in brackets:

* ``renku-host`` is the hostname of the RenkuLab instance
* ``namespace`` is either the username or the group name of the project owner
* ``project`` is the project name
* ``commit-sha-7`` is the first **7** characters of your commit's ``SHA`` 

Let's take the project
`<https://renkulab.io/projects/rok.roskar/flights-tutorial.git>`_ as an example:

* ``renku-host``: ``renkulab.io``
* ``namespace``: ``rok.roskar``
* ``project``: ``flights-tutorial``
* ``commit-sha-7`` of the latest commit can be retrieved by running:

.. code-block:: console

    $ git rev-parse origin/HEAD | cut -c 1-7

    54dc19f

So the full name of this image, including the tag would be
``registry.renkulab.io/rok.roskar/flights-tutorial:54dc19f``.

Alternatively, you can find all available images in GitLab's Container Registry
interface, e.g.,
`<https://renkulab.io/gitlab/rok.roskar/flights-tutorial/container_registry>`_.


Launching the session locally
---------------------------------------------

Finally, we can launch a session locally with the image that has been built 
for the chosen commit. 

.. note::

    If your project is ``private`` or ``internal``, then you need to first login
    to the targeted registry:

    .. code-block:: console

        $ docker login registry.renkulab.io
    
    You will then be asked to enter your ``Username`` and ``Password``:

    * ``Username`` is your username, e.g., ``rok.roskar``
    * ``Password`` is your `Personal Access Tokens
      <https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html>`_
      with at least ``read_registry`` access, which can be created in GitLab,
      e.g., `<https://renkulab.io/gitlab/-/profile/personal_access_tokens>`_

From the project's root directory, run

.. code-block:: shell

    $ imageName=registry.renkulab.io/rok.roskar/flights-tutorial:54dc19f
    $ repoName=$(basename -s .git `git config --get remote.origin.url`)
    $ docker run --rm -ti -v ${PWD}:/work/${repoName} \
      --workdir /work/${repoName} -p 8888:8888 \
      ${imageName} jupyter lab --ip=0.0.0.0

Replace ``imageName`` here with whatever image you derived for your project and
commit above (or if you built your own image, the image/tag combo you used).
This command instructs docker to run the image from the remote registry and to
override its default command with ``jupyter lab``. It also sets the port (``-p``
flag), mounts the current directory into the container (``-v``) and sets that as
the working directory (``--workdir``). Once the image downloads and the
container is created, you will see a series of log messages ending in something
like:

.. code-block:: console

    To access the notebook, open this file in a browser:
        file:///home/jovyan/.local/share/jupyter/runtime/nbserver-24-open.html
    Or copy and paste one of these URLs:
        http://c1e432281137:8888/?token=616bc995658cb9f46673a8fcf486d5c0468f6c6058deb645
     or http://127.0.0.1:8888/?token=616bc995658cb9f46673a8fcf486d5c0468f6c6058deb645

To access the running environment, copy the last of these links (starting with
``https://127.0.0.1``) into your browser and you should drop straight into the
jupyter lab session. The rest should feel rather familiar - your environment
should be identical to what you are used to seeing in your RenkuLab sessions.

In the jupyterlab session, you can change the URL end-point from ``/lab`` to
``/rstudio`` for RStudio projects, or ``/vnc`` for VNC projects.


