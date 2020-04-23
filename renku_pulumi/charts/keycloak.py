import base64

from jinja2 import Template

import pulumi
from pulumi import Output
from pulumi_kubernetes.core.v1 import Secret
from pulumi_kubernetes.helm.v2 import Chart, ChartOpts, FetchOpts
from pulumi_random.random_password import RandomPassword

from deepmerge import always_merger


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

default_chart_values = {
    "test": {"enabled": False},
    "createDemoUser": False,
    "initRealm": {"image": {"repository": "renku/init-realm", "tag": "latest"}},
    "keycloak": {
        "existingSecret": "keycloak-password-secret",
        "existingSecretKey": "keycloak-password",
        "service": {"type": "ClusterIP", "port": 80},
        "persistence": {},
        "test": {"enabled": False},
        "livenessProbe": {"initialDelaySeconds": 180},
        "readinessProbe": {"initialDelaySeconds": 120},
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


def b64encode(s):
    """This is already in utils.py but pulumi doesn't allow full packages, so
     we can't import from there."""
    return base64.b64encode(s.encode()).decode("ascii")


def keycloak_secrets(global_config):
    config = pulumi.Config()

    keycloak_config = pulumi.Config("keycloak")
    values = keycloak_config.get_object("values") or {}

    values = always_merger.merge(default_chart_values, values)

    k8s_config = pulumi.Config("kubernetes")

    keycloak_db_password = config.get("keycloak_db_password")

    if not keycloak_db_password:
        keycloak_db_password = RandomPassword(
            "keycloak_db_password", length=64, special=False, number=True, upper=True
        )

    keycloak_postgres_secret = Secret(
        "renku-keycloak-postgres",
        metadata={
            "name": "renku-keycloak-postgres",
            "labels": {"app": pulumi.get_project(), "release": pulumi.get_stack()},
        },
        type="Opaque",
        data={
            "keycloak-postgres-password": Output.from_input(
                keycloak_db_password
            ).result.apply(lambda p: b64encode(p))
        },
        opts=pulumi.ResourceOptions(delete_before_replace=True),
    )

    keycloak_password = config.get("keycloak_password")

    if not keycloak_password:
        keycloak_password = RandomPassword(
            "keycloak_password", length=64, special=False, number=True, upper=True
        )

    keycloak_password = Output.from_input(keycloak_password)

    pulumi.export("keycloak-admin-password", keycloak_password.result)

    keycloak_password_secret = Secret(
        "keycloak-password-secret",
        metadata={
            "name": "keycloak-password-secret",
            "labels": {"app": pulumi.get_project(), "release": pulumi.get_stack()},
        },
        type="Opaque",
        data={
            "keycloak-password": keycloak_password.result.apply(lambda p: b64encode(p))
        },
        opts=pulumi.ResourceOptions(delete_before_replace=True),
    )

    user_secret_name = "{}-{}-keycloak".format(pulumi.get_stack(), pulumi.get_project())

    users = b64encode("[]")

    if "createDemoUser" in values["keycloak"] and values["keycloak"]["createDemoUser"]:
        client_password = RandomPassword(
            "keycloak_demo_password", length=32, special=True, number=True, upper=True
        )

        users = b64encode(KEYCLOAK_USERS_TEMPLATE.render(password=client_password))

    users_data = {
        "global": {**global_config, **global_config["global"]},
        "gitlab_enabled": config.get_bool("gitlab_enabled") or False,
    }

    keycloak_user_secret = Secret(
        user_secret_name,
        metadata={
            "name": user_secret_name,
            "labels": {"app": pulumi.get_project(), "release": pulumi.get_stack()},
        },
        type="Opaque",
        data={
            "keycloak-username": b64encode(values["keycloak"]["username"]),
            "clients": pulumi.Output.from_input(users_data).apply(
                lambda v: b64encode(KEYCLOAK_CLIENTS_TEMPLATE.render(**v))
            ),  # b64encode(KEYCLOAK_CLIENTS_TEMPLATE.render(**users_data)),
            "users": users,
        },
        opts=pulumi.ResourceOptions(delete_before_replace=True),
    )

    pulumi.export("keycloak-admin-username", values["keycloak"]["username"])

    return keycloak_postgres_secret, keycloak_password_secret, keycloak_user_secret


def keycloak(config, global_config, chart_reqs, postgres, dependencies=[]):
    keycloak_config = pulumi.Config("keycloak")
    values = keycloak_config.get_object("values") or {}

    stack = pulumi.get_stack()

    if postgres:
        default_chart_values["keycloak"]["persistence"][
            "dbHost"
        ] = postgres.get_resource(
            "extensions/v1beta1/Deployment", "{}-postgresql".format(stack)
        ).metadata[
            "name"
        ]

    values = always_merger.merge(default_chart_values, values)

    global_config["keycloak"] = values

    values["global"] = global_config["global"]

    chart_repo = chart_reqs.get("keycloak", "repository")
    if chart_repo.startswith("http"):
        repo = None
        fetchopts = FetchOpts(repo=chart_repo)
    else:
        repo = chart_repo
        fetchopts = None

    dependencies.append(postgres)

    dependencies = [d for d in dependencies if d]
    return Chart(
        "{}-keycloak".format(pulumi.get_stack()),
        config=ChartOpts(
            chart="keycloak",
            repo=repo,
            fetch_opts=fetchopts,
            version=chart_reqs.get("keycloak", "version"),
            values=values,
        ),
        opts=pulumi.ResourceOptions(depends_on=dependencies),
    )
