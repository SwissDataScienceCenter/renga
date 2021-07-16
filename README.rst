..
    Copyright 2017-2021 - Swiss Data Science Center (SDSC)
    A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
    Eidgenössische Technische Hochschule Zürich (ETHZ).

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License... raw:: html

.. _renku:

RENKU (連句)
============

.. image:: https://github.com/SwissDataScienceCenter/renku/actions/workflows/deploy.yml/badge.svg
   :target: https://github.com/SwissDataScienceCenter/renku/actions/workflows/deploy.yml

.. image:: https://readthedocs.org/projects/renku/badge/
    :target: http://renku.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discourse/status?server=https%3A%2F%2Frenku.discourse.group
    :target: https://renku.discourse.group/
    :alt: Discourse

.. image:: https://img.shields.io/gitter/room/SwissDataScienceCenter/renku
    :target: https://gitter.im/SwissDataScienceCenter/renku
    :alt: Gitter

**The Renku Project** is a platform that bundles together various tools for
reproducible and collaborative data analysis projects. It is aimed at
independent researchers and data scientists as well as labs, collaborations, and
courses and workshops. Renku can be used by anyone who deals with data, whether
they are a researcher, data analyst, project owner, or data provider.

Renku promotes **reproducibility** by providing tools to track your analysis
workflows and save them together with your versioned data, code, and
environment specification. Every result can be replayed either to repeat a
calculation or to re-execute on new data or with a different choice of
parameters.

Renku encourages **reusability** by storing and querying the connections between
datasets, code executions, and results in a Knowledge Graph. Producers and
consumers of analysis artifacts can always recover the full provenance of a
result, establishing trust and reducing boilerplate.

Renku stimulates **collaboration** among peers and across disciplines by
guaranteeing that a media-rich discussion space and fully configured, shareable
interactive computational environments are always just a click away.
Collaborators can easily work on projects together or in parallel, combining
their work in a systematic and safe manner.


Getting Started
---------------

The Renku platform consists of `RenkuLab
<https://renku.readthedocs.io/en/latest/introduction/renkulab.html#renkulab>`_,
a web-based application and `Renku
<https://renku.readthedocs.io/en/latest/introduction/renku.html#renku>`_, a
command-line tool for managing code, data, workflows and making practical use of
the Knowledge Graph.

A public instance of **RenkuLab** is available at https://renkulab.io, and there
are several other deployments at various institutions. To start exploring Renku,
feel free to make an account and try it out! You can follow the `first steps
<https://renku.readthedocs.io/en/latest/tutorials/01_firststeps.html>`_ tutorial
or `continue reading about the Renku project
<https://renku.readthedocs.io/en/latest/introduction/index.html#renku-introduction>`_.

Documentation
-------------

* `Tutorials <https://renku.readthedocs.io/en/latest/getting-started.html>`_: how to get your Renku work off the ground
* `Topic Guides <https://renku.readthedocs.io/en/latest/topic-guides.html>`_: discussions about concepts central to Renku
* `How-to Guides <https://renku.readthedocs.io/en/latest/how-to-guides.html>`_: recipes for common use-cases with Renku for users and administrators
* `Reference <https://renku.readthedocs.io/en/latest/reference.html>`_: syntax, structure, architecture, etc.

Contributing
------------

We're happy to receive contributions of all kinds, whether it is an idea for a
new feature, a bug report or a pull request!

Please review our `contributing guidelines
<https://github.com/SwissDataScienceCenter/renku/blob/master/CONTRIBUTING.rst>`_
before submitting a pull request.


Getting in touch
----------------

There are several channels you can use to communicate with us; we monitor all of
them, so your messages will always get to us, but communication will be slightly
more streamlined if you pick a channel that most suits your purpose and needs.

* `discourse <https://renku.discourse.group>`_: questions concerning renkulab or
  renku CLI usage, release notes

* `github <https://github.com/SwissDataScienceCenter/renku>`_ & `renku
  (CLI) <https://github.com/SwissDataScienceCenter/renku-python>`_: create
  platform-usability and software-bug issues

* `gitter <https://gitter.im/SwissDataScienceCenter/renku>`_: communicate with
  the team

Renku is developed as an open source project by the Swiss Data Science Center in
a team split between EPFL and ETHZ.


Project structure
-----------------

The Renku project consists of several sub-repositories:

- `renku-gateway <https://github.com/SwissDataScienceCenter/renku-gateway>`_:
  a simple API gateway

- `renku-graph <https://github.com/SwissDataScienceCenter/renku-graph>`_:
  Knowledge Graph services

- `renku-notebooks <https://github.com/SwissDataScienceCenter/renku-notebooks>`_:
  a lightweight service for handling interactive notebooks through JupyterHub

- `renku-jupyter <https://github.com/SwissDataScienceCenter/renku-jupyter>`_:
  base images for interactive sessions

- `renku-python <https://github.com/SwissDataScienceCenter/renku-python>`_:
  the Python CLI, SDK, and core backend service

- `renku-ui <https://github.com/SwissDataScienceCenter/renku-ui>`_: web front-end

- `renku-project-templates <https://github.com/SwissDataScienceCenter/renku-project-templates>`_:
  base templates used for instantiating renku projects.

- `renkulab-docker <https://github.com/SwissDataScienceCenter/renkulab-docker>`_: docker
  images used for renku sessions.
