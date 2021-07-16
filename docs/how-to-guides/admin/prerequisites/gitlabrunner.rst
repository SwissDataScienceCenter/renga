.. _gitlabrunner:

GitLab-runner configuration
===========================

In order for GitLab to build images that later will be used for launching the Jupyter Notebooks, you need to configure a node that runs a GitLab Runner.

The following are the steps needed for setting up a GitLab Runner in a docker container. Alternatively you can install and run it directly in a VM, see `GitLab documentation <https://docs.gitlab.com/runner/install/linux-repository.html>`_.

1. Run GitLab Runner
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ sudo docker run -d --name <gitlab-runner-name> --restart always \
     -v /srv/gitlab-runner/config:/etc/gitlab-runner \
     -v /var/run/docker.sock:/var/run/docker.sock \
     gitlab/gitlab-runner:latest


2. Register the GitLab Runner with GitLab in Renku
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For this step you need GitLab to be running first. You can do this step after deploying Renku.

We recommend configuring at least one shared runner for Renku and, additionally, other types of runners as needed.

To run the following command first get the registration token from https://renku.mydomain.ch/gitlab/admin/runners

.. code-block:: bash

   $ sudo docker exec -ti <gitlab-runner-name> gitlab-runner \
     register -n -u https://<renku.mydomain.ch>/gitlab/ \
     --name gitlab/gitlab-runner -r  <TOKEN_FROM_GITLAB> \
     --executor docker --locked=false  --run-untagged=true \
     --tag-list=image-build --docker-image="docker:stable"

3. Configure GitLab Runner to support more concurrent jobs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Login to the VM and edit the gitlab-runner config file.

.. code-block:: bash

   $ sudo vi /srv/gitlab-runner/config/config.toml

- Add the desired quantity of runners.

.. code-block:: bash

   concurrent = 10

4. (Optional) Configure a way to clean up disk
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Even if you provide sufficient storage space for the GitLab Runner instance, you might need at some point to clean it up.

To cleanup non used disk space you can use an existing tool like `GitLab Docker cleanup <https://gitlab.com/gitlab-org/gitlab-runner-docker-cleanup>`_ or run a cronjob that periodically prunes non-used images, volumes, containers and networks.
