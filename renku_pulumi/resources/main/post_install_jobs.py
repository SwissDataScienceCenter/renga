import pulumi
from pulumi.resource import CustomTimeouts

from pulumi_kubernetes.batch.v1 import Job


def gitlab_postinstall_job(global_config, cfg_map, renku_secret, postgres_secret, gitlab_chart, dependencies=[]):
    config = pulumi.Config()

    k8s_config = pulumi.Config("kubernetes")

    stack = pulumi.get_stack()
    project = pulumi.get_project()

    renku_name = cfg_map.metadata['name']

    name = "{}-post-install-gitlab".format(stack)

    # force dependency for helm chart, see https://github.com/pulumi/pulumi-kubernetes/issues/861 for issue
    gitlab_deployment = gitlab_chart.resources.apply(
        lambda r: next(s for k, s in r.items() if k.startswith("apps/v1beta2/Deployment")))

    return Job(
        name,
        metadata={"labels": {"app": pulumi.get_project(), "release": stack}},
        spec={
            "template": {
                "metadata": {
                    "name": name,
                    "labels": {"app": pulumi.get_project(), "release": stack},
                    "dummy_dependency": gitlab_deployment.metadata['name'],
                },
                "spec": {
                    "restartPolicy": "Never",
                    "containers": [
                        {
                            "name": "configure-gitlab",
                            "image": "postgres:9.6",
                            "command": ["/bin/bash", "/scripts/init-gitlab.sh"],
                            "volumeMounts": [
                                {
                                    "name": "init",
                                    "mountPath": "/scripts",
                                    "readOnly": True,
                                }
                            ],
                            "env": [
                                {
                                    "name": "PGDATABASE",
                                    "value": global_config["global"]["gitlab"][
                                        "postgresDatabase"
                                    ],
                                },
                                {
                                    "name": "PGUSER",
                                    "value": global_config["global"]["gitlab"][
                                        "postgresUser"
                                    ],
                                },
                                {
                                    "name": "PGHOST",
                                    "value": "{}-postgresql".format(stack),
                                },
                                {
                                    "name": "PGPASSWORD",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": postgres_secret.metadata["name"],
                                            "key": "gitlab-postgres-password",
                                        }
                                    },
                                },
                                {
                                    "name": "JUPYTERHUB_AUTH_GITLAB_CLIENT_SECRET",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": renku_secret.metadata['name'],
                                            "key": "jupyterhub-auth-gitlab-client-secret",
                                        }
                                    },
                                },
                                {
                                    "name": "GATEWAY_GITLAB_CLIENT_SECRET",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": renku_secret.metadata['name'],
                                            "key": "gateway-gitlab-client-secret",
                                        }
                                    },
                                },
                            ],
                        }
                    ],
                    "volumes": [{"name": "init", "configMap": {"name": renku_name}}],
                }
            }
        },
        opts=pulumi.ResourceOptions(depends_on=dependencies, custom_timeouts=CustomTimeouts(create="30m")),
    )


def keycloak_postinstall_job(global_config, keycloak_user_secret, dependencies=[]):
    config = pulumi.Config()

    k8s_config = pulumi.Config("kubernetes")

    stack = pulumi.get_stack()
    project = pulumi.get_project()

    renku_name = "{}-{}".format(stack, project)

    name = "{}-post-install-keycloak".format(stack)

    dependencies = [d for d in dependencies if d]

    return Job(
        name,
        metadata={"labels": {"app": pulumi.get_project(), "release": stack}},
        spec={
            "template": {
                "metadata": {
                    "name": name,
                    "labels": {"app": pulumi.get_project(), "release": stack},
                },
                "spec": {
                    "restartPolicy": "Never",
                    "containers": [
                        {
                            "name": "init-keycloak",
                            "image": "{}:{}".format(
                                global_config["keycloak"]["initRealm"]["image"][
                                    "repository"
                                ],
                                global_config["keycloak"]["initRealm"]["image"]["tag"],
                            ),
                            "command": ["python"],
                            "args": [
                                "/app/init-realm.py",
                                "--admin-user=$(KEYCLOAK_ADMIN_USER)",
                                "--admin-password=$(KEYCLOAK_ADMIN_PASSWORD)",
                                "--keycloak-url=$(KEYCLOAK_URL)",
                                "--users-file=/app/data/users",
                                "--clients-file=/app/data/clients",
                            ],
                            "volumeMounts": [
                                {
                                    "name": "realm-data",
                                    "mountPath": "/app/data",
                                    "readOnly": True,
                                }
                            ],
                            "env": [
                                {
                                    "name": "KEYCLOAK_URL",
                                    "value": "{}://{}/auth/".format(
                                        global_config["http"],
                                        global_config["global"]["renku"]["domain"],
                                    ),  # TODO: where does this value come from?
                                },
                                {
                                    "name": "KEYCLOAK_ADMIN_USER",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": keycloak_user_secret.metadata[
                                                "name"
                                            ],
                                            "key": "keycloak-username",
                                        }
                                    },
                                },
                                {
                                    "name": "KEYCLOAK_ADMIN_PASSWORD",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": "keycloak-password-secret",
                                            "key": "keycloak-password",
                                        }
                                    },
                                },
                                {"name": "PYTHONUNBUFFERED", "value": "0"},
                            ],
                        }
                    ],
                    "volumes": [
                        {
                            "name": "realm-data",
                            "secret": {
                                "secretName": keycloak_user_secret.metadata["name"]
                            },
                        }
                    ],
                },
            }
        },
        opts=pulumi.ResourceOptions(depends_on=dependencies),
    )


def postgres_postinstall_job(
    global_config, graph_db_secret, graph_token_secret, cfg_map, gitlab_postgres_secret=None, dependencies=[]
):
    config = pulumi.Config()

    k8s_config = pulumi.Config("kubernetes")

    stack = pulumi.get_stack()
    project = pulumi.get_project()

    renku_name = "{}-{}".format(stack, project)

    name = "{}-post-install-postgres".format(stack)

    dependencies = [d for d in dependencies if d]

    volume_mounts = [
        {"name": "scripts", "mountPath": "/scripts", "readOnly": True},
        {"name": "passwords", "mountPath": "/passwords", "readOnly": True},
        {
            "name": "keycloak-postgres",
            "mountPath": "/keycloak-postgres",
            "readOnly": True,
        },
        {
            "name": "jupyterhub-postgres",
            "mountPath": "/jupyterhub-postgres",
            "readOnly": True,
        },
        {
            "name": "graph-db-postgres",
            "mountPath": "/graph-db-postgres",
            "readOnly": True,
        },
        {
            "name": "graph-token-postgres",
            "mountPath": "/graph-token-postgres",
            "readOnly": True,
        },
    ]

    volumes = [
        {"name": "scripts", "configMap": {"name": cfg_map.metadata["name"]}},
        {"name": "passwords", "secret": {"secretName": renku_name}},
        {
            "name": "keycloak-postgres",
            "secret": {"secretName": "renku-keycloak-postgres"},
        },
        {
            "name": "jupyterhub-postgres",
            "secret": {"secretName": "renku-jupyterhub-postgres"},
        },
        {
            "name": "graph-db-postgres",
            "secret": {"secretName": graph_db_secret.metadata["name"]},
        },
        {
            "name": "graph-token-postgres",
            "secret": {"secretName": graph_token_secret.metadata["name"]},
        },
    ]

    if config.get_bool("gitlab_enabled"):
        volume_mounts.extend(
            [
                {
                    "name": "gitlab-postgres",
                    "mountPath": "/gitlab-postgres",
                    "readOnly": True,
                },
            ]
        )

        volumes.extend(
            [
                {
                    "name": "gitlab-postgres",
                    "secret": {"secretName": gitlab_postgres_secret.metadata["name"]}
                },
            ]
        )

    return Job(
        name,
        metadata={"labels": {"app": pulumi.get_project(), "release": stack}},
        spec={
            "template": {
                "metadata": {
                    "name": name,
                    "labels": {"app": pulumi.get_project(), "release": stack},
                },
                "spec": {
                    "restartPolicy": "Never",
                    "containers": [
                        {
                            "name": "init-databases",
                            "image": "{}:{}".format(
                                global_config["postgres"]["image"],
                                global_config["postgres"]["imageTag"],
                            ),
                            "command": ["/bin/bash", "/scripts/init-postgres.sh"],
                            "volumeMounts": volume_mounts,
                            "env": [
                                {
                                    "name": "PGDATABASE",
                                    "value": global_config["postgres"][
                                        "postgresDatabase"
                                    ],
                                },
                                {
                                    "name": "PGUSER",
                                    "value": global_config["postgres"]["postgresUser"],
                                },
                                {
                                    "name": "PGHOST",
                                    "value": "{}-postgresql".format(stack),
                                },
                                {
                                    "name": "PGPASSWORD",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": "{}-postgresql".format(stack),
                                            "key": "postgres-password",
                                        }
                                    },
                                },
                            ],
                        }
                    ],
                    "volumes": volumes,
                },
            }
        },
        opts=pulumi.ResourceOptions(depends_on=dependencies),
    )
