..
    Copyright 2017-2018 - Swiss Data Science Center (SDSC)
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

RENKU (連句)
============

.. image:: https://img.shields.io/travis/SwissDataScienceCenter/renku.svg
   :target: https://travis-ci.org/SwissDataScienceCenter/renku

.. image:: https://readthedocs.org/projects/renku/badge/
    :target: http://renku.readthedocs.io/en/latest/
    :alt: Documentation Status

**Renku** is a highly-scalable & secure open software platform designed to
foster multidisciplinary data (science) collaboration.

The platform allows practitioners to:

* Securely manage, share and process large-scale data across untrusted
  parties operating in a federated environment.

* Capture complete lineage automatically up to the original raw data for
  detailed traceability (auditability & reproducibility).


Starting the platform
---------------------

For local development and testing, we provide a script that takes care
of all the boilerplate. To start Renku on your laptop, you will need
`minikube <https://kubernetes.io/docs/setup/minikube/>`_ installed.

.. code:: console

    $ make minikube-deploy

You can find more details about the minikube setup in the `development on minikube
<https://renku.readthedocs.io/en/latest/developer/setup.html>`_ documentation.

More information about the helm charts can be found in the `charts/README.rst <charts/README.rst>`_ file.

Where to go next
----------------

The full documentation is available at
https://renku.readthedocs.io/en/latest/.

First-time users should try our `first steps
<https://renku.readthedocs.io/en/latest/user/firststeps.html>`_ tutorial.


Contributing
------------

We're happy to receive contributions of all kinds, whether it is an idea for a
new feature, a bug report or a pull request.

Please make sure that the integration tests pass and the documentation builds
without warnings and errors before creating a pull request:

.. code-block:: console

    $ make minikube-deploy
    $ make test

To build the documentation from source:

.. code-block:: console

    $ pip install -r docs/requirements.txt
    $ cd docs && make html


Contact
-------

To submit a bug report or a feature request, please open an issue. For other
inquiries contact the Swiss Data Science Center (SDSC) https://datascience.ch/
