from jinja2 import Template

import pulumi
from pulumi_kubernetes.core.v1 import Secret

from .base_chart import BaseChart


KEYCLOAK_CLIENTS_TEMPLATE = Template(
    """
[
  {
    "clientId": "renku",
    "baseUrl": "{{ global.http }}://{{ global.renku.domain }}",
    "secret": "{{ global.gateway.clientSecret }}",
    "redirectUris": [
        "{{ global.http}}://{{ global.renku.domain }}/*"
    ],
    "webOrigins": [
        "{{ global.http }}://{{ global.renku.domain }}/*"
    ],
    "protocolMappers": [{
      "name": "audience for renku",
      "protocol": "openid-connect",
      "protocolMapper": "oidc-audience-mapper",
      "consentRequired": false,
      "config": {
        "included.client.audience": "renku",
        "id.token.claim": false,
        "access.token.claim": true,
        "userinfo.token.claim": false
      }
    }]
  }

  {% if gitlab_enabled %}
  ,{
    "clientId": "gitlab",
    "baseUrl": "{{ global.http }}://{{ global.renku.domain }}/gitlab",
    "secret": "{{ global.gitlab.clientSecret }}",
    "redirectUris": [
      "{{ global.http }}://{{ global.renku.domain }}/gitlab/users/auth/oauth2_generic/callback"
    ],
    "webOrigins": []
  }
  {% endif %}
]""",
    trim_blocks=True,
    lstrip_blocks=True,
)

KEYCLOAK_USERS_TEMPLATE = Template(
    """
[{
    "username": "demo",
    "password": "{{ password}}",
    "enabled": true,
    "emailVerified": true,
    "firstName": "John",
    "lastName": "Doe",
    "email": "demo@datascience.ch"
  }]""",
    trim_blocks=True,
    lstrip_blocks=True,
)


class KeycloakChart(BaseChart):
    """Keycloak Chart."""

    name = "keycloak"
    default_values_template = {
        "test": {"enabled": False},
        "createDemoUser": False,
        "initRealm": {"image": {"repository": "renku/init-realm", "tag": "latest"}},
        "keycloak": {
            "existingSecret": "keycloak-password-secret",
            "existingSecretKey": "keycloak-password",
            "service": {"type": "ClusterIP", "port": 80},
            "test": {"enabled": False},
            "livenessProbe": {"initialDelaySeconds": 80},
            "readinessProbe": {"initialDelaySeconds": 60},
            "extraInitContainers": """- name: theme-provider
image: renku/keycloak-theme:v1.2
imagePullPolicy: IfNotPresent
command:
- sh
args:
- -c
- |
    echo \"Copying theme...\"
    cp -Rfv /renku_theme/* /theme
volumeMounts:
- name: theme
    mountPath: /theme""",
            "username": "admin",
            "persistence": {
                "deployPostgres": False,
                "dbVendor": "postgres",
                "dbName": "keycloak",
                "dbPort": 5432,
                "dbUser": "keycloak",
                "existingSecret": "renku-keycloak-postgres",
                "existingSecretKey": "keycloak-postgres-password",
            },
            "extraEnv": """- name: PROXY_ADDRESS_FORWARDING
value: \"true\"""",
            "extraVolumes": """- name: theme
emptyDir: {}""",
            "extraVolumeMounts": """- name: theme
mountPath: /opt/jboss/keycloak/themes/renku-theme""",
            "ingress": {"enabled": False},
        },
        "resource": {"requests": {"cpu": "1000m", "memory": "2Gi"}},
    }

    def __init__(self, config, postgres_chart, global_config=None, dependencies=[]):
        self.global_config = global_config

        self.postgres_chart = postgres_chart
        self.init_secrets()
        super().__init__(config, global_config=global_config, dependencies=dependencies)

    @property
    def default_values(self):
        default_values = super().default_values

        if self.postgres_chart:
            stack = pulumi.get_stack()

            default_values["keycloak"]["persistence"][
                "dbHost"
            ] = self.delayed_chart_property(
                self.postgres_chart,
                lambda k, s: k.startswith("extensions/v1beta1/Deployment"),
                "name"
            )

        return default_values

    def init_secrets(self):
        """Initialize secrets needed for this chart."""
        config = pulumi.Config()
        keycloak_db_password = config.get("keycloak_db_password")

        self.keycloak_postgres_secret = Secret(
            "renku-keycloak-postgres",
            metadata={
                "name": "renku-keycloak-postgres",
                "labels": {
                    "app": pulumi.get_project(),
                    "release": pulumi.get_stack()},
            },
            type="Opaque",
            data={
                "keycloak-postgres-password": self.generate_random_password(
                    "keycloak_db_password", 64, keycloak_db_password)
            },
            opts=pulumi.ResourceOptions(delete_before_replace=True),
        )

        keycloak_password = config.get("keycloak_password")

        password = self.generate_random_password(
                    "keycloak_password", 64, keycloak_password)

        pulumi.export("keycloak-admin-password", password)

        self.keycloak_password_secret = Secret(
            "keycloak-password-secret",
            metadata={
                "name": "keycloak-password-secret",
                "labels": {
                    "app": pulumi.get_project(),
                    "release": pulumi.get_stack()},
            },
            type="Opaque",
            data={
                "keycloak-password": password
            },
            opts=pulumi.ResourceOptions(delete_before_replace=True),
        )

        user_secret_name = "{}-{}-keycloak".format(
            pulumi.get_stack(), pulumi.get_project())

        users = self.base64encode("[]")

        if "createDemoUser" in self.values["keycloak"] and self.values["keycloak"]["createDemoUser"]:
            client_password = self.generate_random_password(
                "keycloak_demo_password", 32)

            users = self.base64encode(
                KEYCLOAK_USERS_TEMPLATE.render(password=client_password))

        users_data = {
            "global": {**self.global_config, **self.global_config["global"]},
            "gitlab_enabled": config.get_bool("gitlab_enabled") or False,
        }

        self.keycloak_user_secret = Secret(
            user_secret_name,
            metadata={
                "name": user_secret_name,
                "labels": {
                    "app": pulumi.get_project(),
                    "release": pulumi.get_stack()},
            },
            type="Opaque",
            data={
                "keycloak-username": self.base64encode(
                    self.values["keycloak"]["username"]),
                "clients": pulumi.Output.from_input(users_data).apply(
                    lambda v: self.base64encode(
                        KEYCLOAK_CLIENTS_TEMPLATE.render(**v))
                ),
                "users": users,
            },
            opts=pulumi.ResourceOptions(delete_before_replace=True),
        )

        pulumi.export(
            "keycloak-admin-username", self.values["keycloak"]["username"])
