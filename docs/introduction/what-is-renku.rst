.. _what_is_renku_verbose:

What is Renku?
==============

The Renku Project is a web platform (:ref:`renkulab`) and a command-line
interface (:ref:`renku`) built on top of open source components for researchers,
data scientists, educators, and students to help manage their **data**,
**code**, **workflows**, **provenance**, and **computational environments**.

Renku combines many widely-used open-source tools to equip every project on the
platform with resources that aid reproducibility, reusability and collaboration.
Version control for data and code, containerization for runtime environments and
automatic workflow capture are the core pillars on which the platform is built.

.. _renkulab:

Renkulab
--------

Renkulab is a web platform for creating, storing, working on, and sharing your
collaborative data analysis projects. Our public "flagship" deployment of
Renkulab can be found at renkulab.io_ and is free for anyone to use.

Renkulab is the glue that makes it possible to develop and share your research
entirely in the cloud. You can, directly from a project's homepage on Renkulab,
launch JupyterLab and RStudio sessions (or anything else you might run from a
Docker container) using pre-built templates. You can work on your project and
when you are done push the changes back to the repository for safe storage. Our
pre-built base images also contain the ``renku`` command-line tool so you don't
need to worry about installation and can benefit from provenance tracking right
in the interactive session. Renkulab automatically builds images for your
interactive sessions so the computational environments you or your collaborators
use are always up-to-date.

The main components that make up Renkulab are `GitLab <https://gitlab.com>`_ for
repository management, version control, and continuous-integration pipelines;
`JupyterHub <https://jupyter.org>`_ for interactive sessions; a Knowledge Graph
for search and discovery; a few custom services for all renku-specific tasks
like handling datasets.

Please contact us if you would like to deploy your own instance or see
:ref:`admin-documentation`.


.. _renku:

Renku Client
------------

The ``renku`` command-line client is the powerful complement of the hosted
Renkulab platform. It is a tool for easily capturing your data-science process
as you work, by extending version control to encompass the complete research and
data exploration life-cycle. It lets you manage versioned datasets,
automatically create workflows and keep track of computational environments.
Check out :ref:`first_steps` tutorial for a complete example.

The command-line client is automatically installed in computational environments
on Renkulab, but you can you can follow these `installation instructions`_ if
you need to use it elsewhere.


Datasets
~~~~~~~~

The ``renku`` client can  be used to create "datasets", which are just
collections of data files bundled together and enriched with metadata.

It is easy to create datasets

.. code-block:: shell

  renku dataset create mydataset

add files to the dataset

.. code-block:: shell

  renku dataset add mydataset datafile

and even import existing datasets from public repositories like `Zenodo
<https://zenodo.org/>`_ and `Dataverse <https://dataverse.harvard.edu/>`_:

.. code-block:: shell

  renku dataset import https://zenodo.org/record/3981451

The full metadata of the data repository is preserved and mirrored in the
Knowledge Graph for easy retrieval and search.


Provenance of results
~~~~~~~~~~~~~~~~~~~~~

Capturing the :ref:`provenance of results <provenance>` is critical for understanding
what input data were used, what code was run, and what results were produced.

The ``renku`` client gives researchers and analysts a simple tool to
automatically track provenance and iteratively develop a workflow.

Creating a workflow is done by invoking ``renku run`` in front of any shell command:

.. code-block:: shell

  renku run echo "hello-world!" > hello.txt
  renku run wc hello.txt > hello.wc


.. _renkulab.io: https://renkulab.io

.. _`installation instructions`: https://renku-python.readthedocs.io/en/latest/#installation

.. _`CLI documentation`: https://renku-python.readthedocs.io
