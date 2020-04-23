import pulumi
from pulumi_kubernetes.apps.v1beta2 import Deployment

from .values import gateway_values


def gateway_deployment(
    global_config, values, gateway_secret, gateway_configmap, dependencies=[]
):
    gateway_config = pulumi.Config("gateway")

    k8s_config = pulumi.Config("kubernetes")

    stack = pulumi.get_stack()

    gateway_name = "{}-{}-gateway".format(stack, pulumi.get_project())

    gateway_metadata = {"labels": {"app": gateway_name, "release": stack}}

    servicePort = gateway_config.get_int("port") or 80

    return Deployment(
        gateway_name,
        metadata=gateway_metadata,
        spec={
            "replicas": gateway_config.get_int("replica_count") or 1,
            "selector": {"matchLabels": gateway_metadata["labels"]},
            "template": {
                "metadata": gateway_metadata,
                "spec": {
                    "volumes": [
                        {
                            "name": "config",
                            "configMap": {"name": gateway_configmap.metadata["name"]},
                        }
                    ],
                    "containers": [
                        {
                            "name": "gateway",
                            "image": values["image"],
                            "imagePullPolicy": "IfNotPresent",
                            "ports": [
                                {
                                    "name": "http",
                                    "containerPort": servicePort,
                                    "protocol": "TCP",
                                },
                                {"name": "admin", "containerPort": 8080},
                            ],
                            "args": ["--configfile=/config/traefik.toml"],
                            "volumeMounts": [
                                {"name": "config", "mountPath": "/config"}
                            ],
                            "readinessProbe": {
                                "tcpSocket": {"port": servicePort},
                                "failureThreshold": 1,
                                "initialDelaySeconds": 10,
                                "periodSeconds": 10,
                                "successThreshold": 1,
                                "timeoutSeconds": 2,
                            },
                            "livenessProbe": {
                                "tcpSocket": {"port": servicePort},
                                "failureThreshold": 3,
                                "initialDelaySeconds": 10,
                                "periodSeconds": 10,
                                "successThreshold": 1,
                                "timeoutSeconds": 2,
                            },
                            "resources": values["resources"],
                        }
                    ],
                    "nodeSelector": values["nodeSelector"],
                    "affinity": values["affinity"],
                    "tolerations": values["tolerations"],
                },
            },
        },
    )


def gateway_auth_deployment(
    global_config, values, gateway_secret, gateway_configmap, redis, dependencies=[]
):
    config = pulumi.Config()
    gateway_config = pulumi.Config("gateway")

    if config.get_bool("dev"):
        values["graph"]["sparql"]["username"] = "renku"
        values["graph"]["sparql"]["password"] = global_config["graph"]["jena"]["users"][
            "renku"
        ]["password"]

    k8s_config = pulumi.Config("kubernetes")

    stack = pulumi.get_stack()

    auth_name = "{}-{}-gateway-auth".format(stack, pulumi.get_project())

    auth_metadata = {
        "labels": {
            "app": auth_name,
            "release": stack,
            "{}-redis-gw-redis-client".format(stack): "true",
        }
    }

    gateway_url = values["hostName"] or "{}://{}".format(
        global_config["http"], global_config["global"]["renku"]["domain"]
    )

    gitlab_url = values["gitlabUrl"] or "{}://{}/gitlab".format(
        global_config["http"], global_config["global"]["renku"]["domain"]
    )

    if "jupyterhubUrl" not in values:
        values["jupyterhubUrl"] = "{}://{}/jupyterhub".format(
            global_config["http"], global_config["global"]["renku"]["domain"]
        )
    jupyterhub_url = values["jupyterhubUrl"]

    if "keycloakUrl" not in values:
        values["keycloakUrl"] = "{}://{}".format(
            global_config["http"], global_config["global"]["renku"]["domain"]
        )
    keycloak_url = values["keycloakUrl"] or "{}://{}".format(
        global_config["http"], global_config["global"]["renku"]["domain"]
    )

    env = [
        {"name": "HOST_NAME", "value": gateway_url},
        {"name": "GITLAB_URL", "value": gitlab_url},
        {"name": "JUPYTERHUB_URL", "value": jupyterhub_url},
        {"name": "KEYCLOAK_URL", "value": keycloak_url},
        {
            "name": "GITLAB_CLIENT_SECRET",
            "valueFrom": {
                "secretKeyRef": {
                    "name": gateway_secret.metadata["name"],
                    "key": "gitlabClientSecret",
                }
            },
        },
        {
            "name": "GITLAB_CLIENT_ID",
            "value": values["gitlabClientId"]
            or global_config["global"]["gateway"]["gitlabClientId"],
        },
        {
            "name": "JUPYTERHUB_CLIENT_SECRET",
            "valueFrom": {
                "secretKeyRef": {
                    "name": gateway_secret.metadata["name"],
                    "key": "jupyterhubClientSecret",
                }
            },
        },
        {"name": "JUPYTERHUB_CLIENT_ID", "value": values["jupyterhub"]["clientId"]},
        {
            "name": "GATEWAY_SERVICE_PREFIX",
            "value": values["servicePrefix"] if "servicePrefix" in values else "/api/",
        },
        {
            "name": "GATEWAY_REDIS_HOST",
            "value": redis.get_resource(
                "apps/v1beta2/StatefulSet", "{}-redis-gw-redis-master".format(stack)
            ).metadata["name"],
        },
        {
            "name": "GATEWAY_SECRET_KEY",
            "valueFrom": {
                "secretKeyRef": {
                    "name": gateway_secret.metadata["name"],
                    "key": "gatewaySecret",
                }
            },
        },
        {
            "name": "GATEWAY_ALLOW_ORIGIN",
            "value": values["allowOrigin"] if "allowOrigin" in values else "",
        },
        {
            "name": "OIDC_CLIENT_ID",
            "value": values["oidcClientId"] if "oidcClientId" in values else "renku",
        },
        {
            "name": "OIDC_CLIENT_SECRET",
            "valueFrom": {
                "secretKeyRef": {
                    "name": gateway_secret.metadata["name"],
                    "key": "oidcClientSecret",
                }
            },
        },
        {
            "name": "SPARQL_ENDPOINT",
            "value": values["graph"]["sparql"]["endpoint"]
            if "endpoint" in values["graph"]["sparql"]
            else "http://{}-jena:3030/{}/sparql".format(
                stack, k8s_config.require("namespace")
            ),
        },
        {"name": "SPARQL_USERNAME", "value": values["graph"]["sparql"]["username"]},
        {"name": "SPARQL_PASSWORD", "value": values["graph"]["sparql"]["password"]},
        {
            "name": "WEBHOOK_SERVICE_HOSTNAME",
            "value": values["graph"]["webhookService"]["hostname"]
            if values["graph"]["webhookService"]
            and "hostname" in values["graph"]["webhookService"]
            and values["graph"]["webhookService"]["hostname"]
            else "http://{}-graph-webhook-service".format(stack),
        },
    ]

    if "realm" in global_config["global"]["keycloak"]:
        env.append(
            {
                "name": "KEYCLOAK_REALM",
                "value": global_config["global"]["keycloak"]["realm"],
            }
        )

    dependencies = [d for d in dependencies if d]

    return Deployment(
        auth_name,
        metadata=auth_metadata,
        spec={
            "replicas": gateway_config.get_int("replica_count") or 1,
            "selector": {"matchLabels": auth_metadata["labels"]},
            "template": {
                "metadata": auth_metadata,
                "spec": {
                    "containers": [
                        {
                            "name": "gateway",
                            "image": values["auth_image"],
                            "imagePullPolicy": "IfNotPresent",
                            "ports": [
                                {
                                    "name": "http",
                                    "containerPort": 5000,
                                    "protocol": "TCP",
                                }
                            ],
                            "env": env,
                            "readinessProbe": {
                                "httpGet": {"path": "/health", "port": "http"},
                                "initialDelaySeconds": 10,
                                "periodSeconds": 10,
                            },
                            "livenessProbe": {
                                "httpGet": {"path": "/health", "port": "http"},
                                "initialDelaySeconds": 10,
                                "periodSeconds": 10,
                            },
                            "resources": gateway_config.get_object("resources") or {},
                        }
                    ],
                    "nodeSelector": values["nodeSelector"],
                    "affinity": values["affinity"],
                    "tolerations": values["tolerations"],
                },
            },
        },
        opts=pulumi.ResourceOptions(depends_on=dependencies),
    )
