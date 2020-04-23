import json

from jinja2 import Template
import pulumi
from pulumi import Output
from pulumi_kubernetes.core.v1 import Secret
from pulumi_random.random_password import RandomPassword

from ..utils import b64encode


def gitlab_secrets():
    config = pulumi.Config()

    k8s_config = pulumi.Config("kubernetes")

    gitlab_db_password = config.get("gitlab_db_password")

    if not gitlab_db_password:
        gitlab_db_password = RandomPassword(
            "gitlab_db_password", length=64, special=False, number=True, upper=True
        )

    gitlab_postgres_secret = Secret(
        "{}-gitlab-postgres".format(pulumi.get_stack()),
        metadata={
            "labels": {"app": pulumi.get_project(), "release": pulumi.get_stack()}
        },
        type="Opaque",
        data={
            "gitlab-postgres-password": Output.from_input(
                gitlab_db_password
            ).result.apply(lambda p: b64encode(p))
        },
    )

    gitlab_sudo_token = config.get("gitlab_sudo_token")

    if not gitlab_sudo_token:
        gitlab_sudo_token = RandomPassword(
            "gitlab_sudo_token", length=64, special=False, number=True, upper=True
        )

    gitlab_sudo_secret = Secret(
        "{}-gitlab-sudo".format(pulumi.get_stack()),
        metadata={
            "labels": {"app": pulumi.get_project(), "release": pulumi.get_stack()}
        },
        type="Opaque",
        data={
            "gitlab-sudo-token": Output.from_input(gitlab_sudo_token).result.apply(
                lambda p: b64encode(p)
            )
        },
    )

    return gitlab_postgres_secret, gitlab_sudo_secret


def graph_secrets():
    config = pulumi.Config()

    k8s_config = pulumi.Config("kubernetes")

    graph_db_password = config.get("graph_db_password")

    if not graph_db_password:
        graph_db_password = RandomPassword(
            "graph_db_password", length=64, special=False, number=True, upper=True
        )

    graph_db_postgres_secret = Secret(
        "{}-graph-db-postgres".format(pulumi.get_stack()),
        metadata={
            "labels": {"app": pulumi.get_project(), "release": pulumi.get_stack()}
        },
        type="Opaque",
        data={
            "graph-dbEventLog-postgresPassword": Output.from_input(
                graph_db_password
            ).result.apply(lambda p: b64encode(p))
        },
    )

    graph_token_password = config.get("graph_token_postgres_password")

    if not graph_token_password:
        graph_token_password = RandomPassword(
            "graph_token_password", length=64, special=False, number=True, upper=True
        )

    graph_token_postgres_secret = Secret(
        "{}-graph-token-postgres".format(pulumi.get_stack()),
        metadata={
            "labels": {"app": pulumi.get_project(), "release": pulumi.get_stack()}
        },
        type="Opaque",
        data={
            "graph-tokenRepository-postgresPassword": Output.from_input(
                graph_token_password
            ).result.apply(lambda p: b64encode(p))
        },
    )

    return graph_db_postgres_secret, graph_token_postgres_secret


def jupyterhub_secrets():
    config = pulumi.Config()

    k8s_config = pulumi.Config("kubernetes")

    jupyterhub_db_password = config.get("jupyterhub_db_password")

    if not jupyterhub_db_password:
        jupyterhub_db_password = RandomPassword(
            "jupyterhub_db_password", length=64, special=False, number=True, upper=True
        )

    return Secret(
        "renku-jupyterhub-postgres",
        metadata={
            "name": "renku-jupyterhub-postgres",
            "labels": {"app": pulumi.get_project(), "release": pulumi.get_stack()},
        },
        type="Opaque",
        data={
            "jupyterhub-postgres-password": Output.from_input(
                jupyterhub_db_password
            ).result.apply(lambda p: b64encode(p))
        },
        opts=pulumi.ResourceOptions(delete_before_replace=True),
    )


def renku_secret(global_config):
    config = pulumi.Config()

    notebooks_values = pulumi.Config("notebooks")
    notebooks_values = notebooks_values.require_object("values")

    k8s_config = pulumi.Config("kubernetes")

    gitlab_client_secret = global_config["global"]["gitlab"].get("clientAppSecret")

    if not gitlab_client_secret:
        gitlab_client_secret = RandomPassword(
            "gitlab_client_secret", length=64, special=True, number=True, upper=True
        )

    gateway_gitlab_client_secret = global_config["global"]["gateway"][
        "gitlabClientSecret"
    ]

    if not gateway_gitlab_client_secret:
        gateway_gitlab_client_secret = RandomPassword(
            "gateway_gitlab_client_secret",
            length=64,
            special=True,
            number=True,
            upper=True,
        )

    data = {
        "jupyterhub-auth-gitlab-client-secret": Output.from_input(
            gitlab_client_secret
        ).apply(lambda p: b64encode(p)),
        "gateway-gitlab-client-secret": Output.from_input(
            gateway_gitlab_client_secret
        ).apply(lambda p: b64encode(p)),
    }

    if "users_json" in global_config["global"]["tests"]:
        data["users.json"] = b64encode(
            json.dumps(global_config["global"]["tests"]["users_json"])
        )

    secret_name = "{}-{}".format(pulumi.get_stack(), pulumi.get_project())

    return Secret(
        secret_name,
        metadata={
            "name": secret_name,
            "labels": {"app": pulumi.get_project(), "release": pulumi.get_stack()},
        },
        type="Opaque",
        data=data,
        opts=pulumi.ResourceOptions(delete_before_replace=True),
    )
