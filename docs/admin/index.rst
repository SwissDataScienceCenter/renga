.. _admin_documentation:

Deploying the Renku platform
============================

This guide will help you deploying and customizing your own Renku instance in a cluster.

Cluster requirements
-----------------------

To deploy Renku in a cluster, you need to have the following prerequisites:

- a `Kubernetes  <https://kubernetes.io/>`_ cluster

.. toctree::
   :maxdepth: 1

   Helm <prerequisites/helm>
   a DNS domain <prerequisites/dns>
   and its certificate (or a cert-manager LetsEncrypt) <prerequisites/certificates>
   NGINX (or other) ingress <prerequisites/nginx>
   a GitLab-runner VM for the docker image builder with sufficient storage <prerequisites/gitlabrunner>

Optionally, you can choose to manage your own instances of the following:

   - using an existing `GitLab instance <https://about.gitlab.com/install/>`_
   - using an existing Keycloak instance

Officially supported versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following component versions have been tested in production.

===================   ============   ============
Renku version         Kubernetes     Helm
===================   ============   ============
0.6.x                 1.14, 1.15     2
0.7.x                 1.16, 1.17     3
===================   ============   ============

Pre-deployment steps
-----------------------

1. (Optional) Stand-alone configurations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   Stand-alone GitLab <configurations/standalone-gitlab>
   Stand-alone Keycloak <configurations/standalone-keycloak>

2. Create and configure Renku PVs and PVCs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All of Renku information is stored in three volumes needed by Jena, Postgresql and GitLab (if not stand-alone).
To this end, persistent volumes and persistent volume claims need to be created. You can leave k8s to dynamically provision these volumes but we advise to create them beforehand and make regular backups.
You can use the following manifest files as examples and apply them through `kubectl`.

   - `Renku PV yaml file <https://github.com/SwissDataScienceCenter/renku-admin-docs/blob/master/renku-pv.yaml>`_
   - `Renku PVC yaml file <https://github.com/SwissDataScienceCenter/renku-admin-docs/blob/master/renku-pvc.yaml>`_

   .. code-block:: console

     $ kubectl create -f renku-pv.yaml
     $ kubectl create ns renku
     $ kubectl -n renku create -f renku-pvc.yaml

Ensure that PVs are added correctly and have the appropriate storage class.

3. Create a renku-values.yaml file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step is very important as it will define the values that helm will use to install your Renku instance.

Basic configuration
^^^^^^^^^^^^^^^^^^^^

The basic Helm configuration file is in the Renku repository: `Renku values file <https://github.com/SwissDataScienceCenter/renku/blob/master/helm-chart/renku/values.yaml>`_

You can use the `make-values.sh <https://github.com/SwissDataScienceCenter/renku/blob/master/helm-chart/example-configurations/make-values.sh>`_ script to generate automatically a minimal Renku values file. You need to provide your DNS and (optionally) your Gitlab URL, application ID and secret.
This script needs bash >=4.0 and openssl installed and the `minimal-values.tmpl <https://github.com/SwissDataScienceCenter/renku/blob/master/helm-chart/example-configurations/minimal-values.tmpl>`_ file

For MacOS:
.. code-block:: bash

  $ brew install bash
  $ brew install openssl

.. code-block:: bash

  $ ./make-values.sh -d renku.mydomain.ch -o renku-values.yaml


After preparing your values and before deploying Renku please make sure to check the following in the values file:

  - the URLs and DNS names are correct
  - all the necessary secrets are configured
  - the ingress configuration is correct
  - add/verify, if necessary, the persistent volume claims

Further configuration
^^^^^^^^^^^^^^^^^^^^^^

You might want to modify some default values, here are some examples:

   * Logged-out users can be given the permission to launch interactive sessions from public notebooks. This feature is turned off by default. For details on how to enable this feature, see the dedicated section below.
   * A custom privacy notice and cookie banner can be configured (as of Renku 0.6.8). See the dedicated section below.
   * Resources requests and limits can be adjusted for the diverse RenkuLab components
   * For deployments that include GitLab you can configure an S3 backend for `lfs objects <https://docs.gitlab.com/ce/administration/lfs/index.html>`_ and `registry <https://docs.gitlab.com/ee/administration/packages/container_registry.html>`_, this configuration can be added in the ``gitlab`` section
   * It is possible to dedicate some nodes for running interactive user sessions.

   .. toctree::
      :maxdepth: 1

      Enabling notebooks for anonymous users <anonymous-sessions>
      Configure privacy notice and cookie banner <privacycookie>
      Configuring the RenkuLab Homepage <homepage>

Deploying RenkuLab
-------------------

1. (Optional) Certificates
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you chose to create a certificate manually instead of using LetsEncrypt or similar, you can create the corresponding TLS secret with the following command:

.. code-block:: bash

   $ kubectl -n renku create secret tls renku-mydomain-ch-tls --cert=certificate.crt --key=certificate.key

Note that ``renku-mydomain-ch-tls`` should correspond to the `ingress TLS value in Renku values file <https://github.com/SwissDataScienceCenter/renku/blob/master/helm-chart/example-configurations/minimal-values.tmpl#L12>`_

2. Deploy RenkuLab
~~~~~~~~~~~~~~~~~~~~

Once all the pieces are in place, you can deploy Renku with the following commands:

.. code-block:: console

    $ helm init
    $ helm repo add renku https://swissdatasciencecenter.github.io/helm-charts/
    $ helm upgrade --install renku renku/renku \
     --namespace renku \
     -f renku-values.yaml \
     --timeout 1800s

During deployment you can check the Renku pods being started.
If deploying for the first time, GitLab and Keycloak take around 15 minutes to get started. It is normal to see other pods of components that depend on these to be in a `CrashLoopBackOff` state.

Once all the pods are correctly running or completed, a `GitLab Runner <prerequisites/gitlabrunner>`_ can be configured.

3. Verifying RenkuLab deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check list:

  * Helm command completed successfully.
  * RenkuLab pods should be all running and jobs completed.
  * RenkuLab pods logs should not show errors.
  * Perform a quick check:
     #. go to your RenkuLab instance domain (this will verify the ingress is working properly)
     #. login with a valid user, you can register a new one (this will verify various authentication steps)
     #. create a project (this will verify further authentication, templates and GitLab runner)
     #. add a dataset (this will verify the core backend, LFS objects, and Knowledge Graph components work)
     #. launch an environment (this will verify the notebooks component and GitLab image registry)
  * You should be now able to follow "First steps"

If some Renku pods are not starting or present some errors please check the troubleshooting page.

.. toctree::
   :maxdepth: 1

   Troubleshooting a RenkuLab deployment <troubleshooting>

4. Acceptance tests (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the Helm deployment ran successfully according to the check list above, you might want to run Renku's acceptance tests.
You simply need to:

  * create a user for testing (with no admin rights) and optionally have an S3 bucket credentials for saving screenshots in case a test fails.
  * fill in the credentials (notably email and password) in the `test section in the values file <https://github.com/SwissDataScienceCenter/renku/blob/master/helm-chart/renku/values.yaml#L595-L620>`_ and update the deployment

  .. code-block:: console

    $ helm upgrade --install renku renku/renku \
     --namespace renku \
     --version <renku-version> \
     -f renku-values.yaml \
     --timeout 1800s

  * run the tests. This will create a test pod that needs around 4GB of RAM available. Note that running the complete acceptance test suit takes around 40 minutes to complete.

  .. code-block:: console

      $ helm test renku \
       --namespace renku \
       --log-file renku-tests.log \
       --timeout 80m

5. Post deployment configurations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After RenkuLab has been deployed you can make some post deployment configurations.

GitLab deployed as part of Renku
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your RenkuLab deployment includes GitLab you need to follow some additional steps to configure an admin user on GitLab.

#. turn off automatic redirection to GitLab by redeploying with the value ``gitlab.oauth.autoSignIn: false``
#. log in as the root user using the password from ``gitlab.password``
#. modify any users you want to modify (e.g. to make them admin)
#. turn the ``autoSignIn`` setting back on

Independent GitLab as identity provider
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the RenkuLab deployment is relying on an existing GitLab instance, this instance could be configured as an identity provider for RenkuLab's keycloak. This way all of the users from the existing GitLab instance can log into RenkuLab with their existing login information.

#. Go to \https://<renku-domain>/auth (or to your stand-alone Keycloak dashboard), login to ``Admin console`` using ``admin`` as username and the decoded password stored in ``keycloak-password-secret``.
#. Add an ``Identity Provider`` of type ``OpenID Connect v1.0``.
#. Set ``Alias`` to <renku-domain>, ``Authorization URL`` to \https://<gitlab-domain>/oauth/authorize, ``Token URL`` to \https://<gitlab-domain>/oauth/token and ``Client ID`` and ``Client Secret`` to the values used in step 1.
#. Click ``Save``. The new Identity Provider should appear and any user from the stand-alone GitLab instance should be able to login.

Upgrading RenkuLab
------------------

To upgrade RenkuLab to a newer version please check the **Upgrading from 0.x.x** section of the `release notes <https://github.com/SwissDataScienceCenter/renku/releases>`_ in case the renku-values.yaml file needs to be modified.
Following, you can upgrade Renku via Helm.

.. code-block:: console

    $ helm repo update
    $ helm upgrade --install renku renku/renku \
     --namespace renku \
     --version <renku-version> \
     -f renku-values.yaml \
     --timeout 1800s
