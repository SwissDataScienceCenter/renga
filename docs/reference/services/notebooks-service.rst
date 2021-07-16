.. _notebooks_service:

Notebooks service
=================

The notebooks service provides an interactive computing environment for every
commit in a project's history to each user that has sufficient access rights.

JupyterHub integration
----------------------

`JupyterHub <https://jupyterhub.readthedocs.io/en/stable/>`_ is a multi-user
server for spawning interactive `Jupyter notebooks <https://jupyter-
notebook.readthedocs.io/en/stable/>`_. Renku uses JupyterHub to manage
sessions and the ``notebooks-service`` extends the standard
JupyterHub functionality by providing tight integration with GitLab.

The notebooks are provided by the JupyterHub server. A new "named" server is
spawned for every unique request. A notebook server launch is initiated by
accessing the
``<PLATFORM_URL>/<JUPYTERHUB_PREFIX>/services/notebooks/<namespace>/<project-
name>/<commit-sha>`` URL. This means that two users collaborating on a project
use the same URL, but each will receive their own notebook server.

By default, a Renku project will include a ``.gitlab-ci.yml`` file that
contains an ``image_build`` stage which creates an image for every push (see the
:ref:`notebooks_image_builds` section below). The
notebook spawner looks for this GitLab CI job and if it exists, the spawner waits
for the job to complete and then launches a notebook server using that image.
If the job does not exist or there is a problem with the image build, a notebook
server is launched with the default notebook image as specified in the
platform configuration options.

The architecture of this setup is presented in the figure below. Blue ovals
represent off-the-shelf services and yellow ovals show heavily
customized or custom-built components.

.. _fig-notebook-service-architecture:

.. graphviz:: /_static/graphviz/notebook_service_architecture.dot


The diagram below illustrates the sequence of events that take place in order
to launch a new notebook using the notebook service:

.. _fig-uml_notebooks_service:

.. uml:: ../../_static/uml/notebook-sequence.uml
   :alt: Sequence diagram of notebook launch from the UI via the Notebooks Service.


.. _notebooks_image_builds:

Image builds
------------

If the Renku repository contains a ``.gitlab-ci.yml`` file the GitLab instance
that the repository is pushed to will try to execute the commands inside this
file. By default, when a ``renku`` project is initialized, ``.gitlab-ci.yml``,
``Dockerfile``, and ``requirements.txt`` are added to the project. On push to the
server, the GitLab runner (if it is configured) will then build the image
with the name ``<gitlab-registry>/<namespace>/<project-name>:<commit-sha>``.
This way we guarantee that the user will have an image available for every
point in the project's history. In future iterations of these services, the
build process will be optimized to avoid superfluous builds and reduce launch
latency to improve the user experience.

The image building component interactions are visualized below.

.. _fig-image-build-architecture:

.. graphviz:: /_static/graphviz/gitlab_components_architecture.dot
