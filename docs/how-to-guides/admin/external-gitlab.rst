.. _external_gitlab:

Deploying Renku with an external GitLab
=======================================

GitLab is a component of the Renku platform. Running it is quite resource-intensive.
For development purposes or if you already have an existing GitLab instance running,
you might want to use this instance as a backend service for Renku.

In the section about :ref:`running Renku locally <running_on_minikube>` we give a
detailed description of how to bring up a local version of the platform using `<gitlab.com>`_
while also using ``gitlab.com`` as an identity provider. Note that in Renku deployments
which include their own GitLab, the dependency is the other way around, meaning
that the Renku GitLab instance uses the Renku Keycloak instance as identity provider.


Caveats
-------

There are known **caveats** for a setup using an external GitLab instance:

- Notebook servers can only be launched from public projects. This is due to the
  fact that the users credentials are needed for pulling images for private
  projects from the GitLab registry. In deployments which include "their own"
  GitLab instance, we use a GitLab API token with sudo permissions for this purpose.
  This is obviously not possible when using an existing GitLab instance that you are
  not managing yourself.

- ``gitlab.com`` limits the total size of each repository to 10 GB (including the files added
  to git-lfs). This is fine for development work but quite restrictive for actual
  Renku projects.

- Depending on how CI runners are configured on the GitLab instance which you are using,
  you might have to adapt the ``.gitlab-ci.yaml`` file in your projects. See the
  :ref:`paragraph on configuring GitLab CI <runner_extra_config>`.


gitlab.com
----------
The extra configuration needed for a deployment against ``gitlab.com`` is in a
specific `values file <https://github.com/SwissDataScienceCenter/renku/blob/master/helm-chart/example-configurations/gitlab_dot_com-gitlab-values.yaml>`_.
This file can also be used as a secondary values file in a Renku deployment which is
running in the cloud.


renkulab.io
-----------
You can also use the GitLab instance of the SDSCs public renku deployment
`<https://renkulab.io/gitlab>`_ as a GitLab backend. The same
`values file <https://github.com/SwissDataScienceCenter/renku/blob/master/helm-chart/example-configurations/gitlab_dot_com-gitlab-values.yaml>`_.
has the necessary configurations for such a deployment indicated. All the steps
necessary for such a setup are identical to the ones when using ``gitlab.com``,
except for the configuration of ``renkulab.io/gitlab`` as the upstream identity provider
for your Keycloak instance. Instead of ``gitlab.com`` pick the generic OICD provider
option and fill in the following information:

+-------------------+------------------------------------------------+
| Field             | Value                                          |
+===================+================================================+
| Alias             | renkulab                                       |
+-------------------+------------------------------------------------+
| Authorization URL | https://renkulab.io/gitlab/oauth/authorize     |
+-------------------+------------------------------------------------+
| Token URL         | https://renkulab.io/gitlab/oauth/token         |
+-------------------+------------------------------------------------+
| Client ID         | [Application Id of GitLab client application]  |
+-------------------+------------------------------------------------+
| Client Secret     | [Secret of GitLab client application]          |
+-------------------+------------------------------------------------+
