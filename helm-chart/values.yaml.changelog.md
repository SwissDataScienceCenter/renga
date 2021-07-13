# `values.yaml` changelog
Necessary changes to the values files for upgrading the Renku chart version are listed here.
For changes that require manual steps other than changing values, please check out [the chart readme](https://github.com/SwissDataScienceCenter/renku/tree/master/helm-chart#upgrading).

Please follow this convention when adding a new row
* `<type: NEW|EDIT|DELETE> - *<resource name>*: <details>`

----
## Unreleased (ui 1.0.0)
* NEW - *ui.homepage* has been added for customizing the content on the RenkuLab home page. See the values.yml file for more detailed documentation.

## Upgrading to Renku 0.8.0 (breaking changes)
* NEW/EDIT *postgresql.persistence.existingClaim* will most likely need to be modified in the course of upgrading your postgresql version. See [these instructions](https://github.com/SwissDataScienceCenter/renku/tree/master/helm-chart/utils/postgres_migrations/version_upgrades/README.md)
* NEW/EDIT/DELETE *gitlab.image.tag* might have to be adjusted as we do a GitLab major version bump in with this release. See [these instructions](https://github.com/SwissDataScienceCenter/renku/tree/master/helm-chart#upgrading-to-080)


## Upgrading to Renku 0.7.13
* NEW - *global.gateway.cliClientSecret* has been added when introducing a new "renku-cli" client application in keycloak. Generate through `openssl rand -hex 32`.


## Upgrading to Renku 0.7.9
* NEW - *ui.uiserverUrl* has been added. The default value is `<domain>/ui-server`.


## Upgrading to Renku 0.7.8 (INCLUDES BREAKING CHANGES!)
* Keycloak chart dependency upgraded from `4.10.2` to `9.8.1`, check out [the instructions](https://github.com/codecentric/helm-charts/tree/master/charts/keycloak#upgrading) on how to upgrade aspects not covered by default in the Renku chart. Most notably, keycloak values are
less nested, so at the level of the Renku chart values, *keycloak.keycloak.X.Y* becomes *keycloak.X.Y*.
* EDIT - the section *keycloak.keycloak.persistence* has been removed. Database connection
details are specified through the *keycloak.extraEnv* and *keycloak.extraEnvFrom* blocks. See
the [Renku values file](https://github.com/SwissDataScienceCenter/renku/blob/master/helm-chart/renku/values.yaml) for reference.
* EDIT - *keycloak.keycloak.username* has been moved to *global.keycloak.user*.


## Upgrading to Renku 0.7.0 (INCLUDES BREAKING CHANGES!)
* EDIT - *postgresql.persistence.existingClaim*: Renku `0.7.0` upgrades the postgres chart dependency, which requires modification of the postgres data volume of existing deployments. See [this helper job manifest](https://github.com/SwissDataScienceCenter/renku/blob/master/helm-chart/utils/migrate-pg-to-bitnami.yaml).
* EDIT - *postgresql.postgresPassword* renamed to *postgresql.postgresqlPassword*.
* DELETE - *minio.enabled*: minio has been removed from the Renku dependencies, deploy minio as a standalone service if you need it.
* DELETE - *ui.templatesRepository*
* NEW - *ui.templates*: the UI project creation has been overhauled and can be configured here.
* NEW - *ui.templates.repositories* - list of renku templates repositories to be used in the ui. Each object contains a `url` pointing to the repository, a `ref` specifying the target tag or commit, a `name` acting as a user friendly short name.
* DELETE - *global.gitlab.sudoToken* - this is no longer needed.
* DELETE - *notebooks.gitlab.registry.secret* - this is no longer needed.
* DELETE - *notebooks.gitlab.registry.token* - this is no longer needed.
* DELETE - *notebooks.gitlab.registry.username* - this is no longer needed.
* DELETE - *gateway.graph* - this is no longer needed.


## Changes on top of Renku 0.6.5
* NEW - *ui.statuspage.id*: the id for the statuspage.io instance. See the values.yml file
for more detailed documentation.

## Changes on top of Renku 0.6.1
Interactive sessions for logged-out users are now possible, see
[the docs](https://renku.readthedocs.io/en/latest/admin/index.html#enabling-notebooks-for-anonymous-users).
* NEW - *global.anonymousSessions.enabled*: set to true to turn on notebook sessions
for logged out users.
* NEW - *global.anonymousSessions.postgresPassword.overwriteOnHelmUpgrade*: set to `true` when upgrading an existing deployment, then back to `false` (default value).

## Changes on top of Renku 0.5.2
* NEW - *ui.sentry*: added Sentry information for logging runtime exceptions

## Changes on top of Renku 0.4.3
* EDIT - *notebooks.serverOptions*: added `<resource>.order` to control ui rendering order. The default values defined in notebooks are now different.
* DELETE - *graph.knowledgeGraph.services.renku.url*: no need for this anymore as it's linked to `global.renku.domain` internally. Ref: [refactor KG remove services renku URL](https://github.com/SwissDataScienceCenter/renku/commit/6d4a0e5cf02833d193f86a38cc14762609fcd9c0)
* DELETE - *keycloak.keycloak.extraVolumes.-name:realm-secret* : need to delete `renku-realm.json` in order to work with [remove realm template](https://github.com/SwissDataScienceCenter/renku/commit/825c10e72d185bfaff78af8c7693d06cd745014c) commit
* EDIT - *global.gitlab.postgresPassword*: now split into `value` and `overwriteOnHelmUpgrade`, set the latter to true to generate a password or set value to use an existing one.
* EDIT - *global.gitlab.sudoToken*: now split into `value` and `overwriteOnHelmUpgrade`, set the latter to true to generate a password or set value to use an existing one.
* EDIT - *global.keycloak.postgresPassword*: now split into `value` and `overwriteOnHelmUpgrade`, set the latter to true to generate a password or set value to use an existing one.
* NEW - *global.keycloak.password*: split into `value` and `overwriteOnHelmUpgrade`, set the latter to true to generate a password or set value to use an existing one.
* DELETE - *keycloak.keycloak.password*: the admin password for keycloak is now provided through a k8s secret which is set in the global values section.
* EDIT - *global.jupyterhub.postgresPassword*: now split into `value` and `overwriteOnHelmUpgrade`, set the latter to true to generate a password or set value to use an existing one.
* EDIT - *global.graph.dbEventLog.postgresPassword*: now split into `value` and `overwriteOnHelmUpgrade`, set the latter to true to generate a password or set value to use an existing one.
* EDIT - *global.graph.tokenRepository.postgresPassword*: now split into `value` and `overwriteOnHelmUpgrade`, set the latter to true to generate a password or set value to use an existing one.
* EDIT - *notebooks.jupyterhub.hub.db.url*: remove the password (between ":" and "@" from the URL).
* EDIT - *notebooks.jupyterhub.hub.db.extraEnv*: due to the inability of helm to merge maps, all extra environment variables must be explicitly provided after the introduction of secrets auto-generation:
```
        extraEnv:
          - name: GITLAB_URL
            value: <your-gitlab-url>
          - name: JUPYTERHUB_SPAWNER_CLASS
            value: spawners.RenkuKubeSpawner
          - name: PGPASSWORD
            valueFrom:
              secretKeyRef:
                name: renku-jupyterhub-postgres
                key: jupyterhub-postgres-password
```
