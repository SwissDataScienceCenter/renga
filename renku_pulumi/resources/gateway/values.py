import pulumi
from pulumi_random.random_password import RandomPassword
from pulumi_random.random_id import RandomId

from deepmerge import always_merger

import base64

default_chart_values = {
    "replicaCount": 1,
    "hostName": None,
    "development": True,
    "rateLimits": {
        "general": {
            "extractorfunc": "request.header.cookie",
            "period": "10s",
            "average": 20,
            "burst": 100,
        }
    },
    "service": {"port": 80, "type": "ClusterIP"},
    "image": "traefik:v2.0.0-alpha4",
    "auth_image": "renku/renku-gateway:0.7.0-991962e",  # "renku/renku-gateway:0.6.0",
    "ingress": {"enabled": False},
    "graph": {"webhookService": None, "sparql": {}},
    "resources": {"requests": {"cpu": "100m", "memory": "512Mi"}},
    "nodeSelector": {},
    "tolerations": [],
    "affinity": {},
    "jupyterhub": {}
}


def gateway_values(global_config):
    """Get gateway values config."""
    config = pulumi.Config()
    gateway_config = pulumi.Config("gateway")
    gateway_values = gateway_config.get_object("values") or {}

    if config.get_bool("dev"):
        default_chart_values["secretKey"] = RandomPassword(
            "gateway_secretkey",
            length=32,
            special=False,
            number=True,
            upper=False,
            lower=True,
        ).result

        default_chart_values["jupyterhub"]["clientSecret"] = RandomId(
                "gateway_jupyterhub_client_secret", byte_length=32
            ).hex

        baseurl = config.get("baseurl")

        if baseurl:
            default_chart_values["gitlabUrl"] = "https://{}/gitlab".format(baseurl)

    default_chart_values["gitlabClientId"] = global_config["global"]["gitlab"][
        "clientAppId"
    ]
    default_chart_values["gitlabClientSecret"] = global_config["global"]["gitlab"][
        "clientAppSecret"
    ]

    gateway_values = always_merger.merge(default_chart_values, gateway_values)
    global_config["gateway"] = gateway_values

    return gateway_values
