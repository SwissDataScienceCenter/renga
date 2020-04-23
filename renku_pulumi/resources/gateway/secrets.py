from ..utils import b64encode

import pulumi
from pulumi_kubernetes.core.v1 import Secret

from .values import gateway_values


def secret(global_config, values):
    config = pulumi.Config("gateway")

    k8s_config = pulumi.Config("kubernetes")

    stack = pulumi.get_stack()

    gateway_name = "{}-{}-gateway".format(stack, pulumi.get_project())

    gateway_metadata = {"labels": {"app": gateway_name, "release": stack}}

    if "oidcClientSecret" not in values:
        values["oidcClientSecret"] = global_config["global"]["gateway"]["clientSecret"]

    if "gitlabClientSecret" not in values:
        values["gitlabClientSecret"] = global_config["global"]["gateway"][
            "gitlabClientSecret"
        ]

    return Secret(
        gateway_name,
        metadata=gateway_metadata,
        type="Opaque",
        data={
            "oidcClientSecret": pulumi.Output.from_input(
                values["oidcClientSecret"]
            ).apply(lambda o: b64encode(o)),
            "gitlabClientSecret": b64encode(values["gitlabClientSecret"]),
            "jupyterhubClientSecret": pulumi.Output.from_input(values["jupyterhub"]["clientSecret"]).apply(lambda o: b64encode(o)),
            "gatewaySecret": pulumi.Output.from_input(values["secretKey"]).apply(
                lambda o: b64encode(o)
            ),
        },
    )
