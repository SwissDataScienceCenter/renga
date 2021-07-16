.. _admin_anonymous-sessions:

Enabling notebooks for anonymous users
--------------------------------------

Interactive sessions launched from public notebooks can be made available to
logged-out users. However, this feature is deactivated by default. In order
to activate it, you need a secondary deployment of the renku-notebooks chart
(including a secondary Jupyterhub as a dependency) to handle the anonymous
("temporary") sessions. Note that this deployment has to run in a separate
kubernetes namespace because of the way Jupyterhub operates.

0. The following steps assume that you have a local clone of the Renku repository and :code:`pipenv` installed.

1. Set :code:`global.anonymousSessions.enabled: true` in your values.yaml file. If you are
   updating an existing deployment you have to set :code:`global.anonymousSessions.postgresPassword.overwriteOnHelmUpgrade: true`
   for the upgrade and then back to `false` for upcoming deployments.

2. Deploy renkulab (or update your existing deployment) just as you would otherwise.

3. At the end of the deployment process, you will see a rendered command which will invoke a script
   :code:`deploy-tmp-notebooks.py`. This script will

     - Create a secondary namespace
     - Copy the secret :code:`renku-jupyterhub-tmp-postgres` to the secondary namespace
     - Get the supplied values from your helm renku deployment and derive a corresponding
       one for your your secondary renku-notebooks deployment.
     - Deploy the secondary renku-notebooks instance to the newly created namespace.

   Some values for the secondary notebooks-deployment will likely differ from the corresponding ones
   used in the primary deployment (such as the notebook server resource options available to users).
   You can provide those using the flag :code:`--extra-values <path-to-values-file>.yaml`. Type
   :code:`pipenv run ./deploy-tmp-notebooks.py --help` for more useful options of that script.
