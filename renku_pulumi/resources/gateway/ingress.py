import pulumi
from pulumi_kubernetes.extensions.v1beta1 import Ingress

from .values import gateway_values


def ingress(global_config, values):
    config = pulumi.Config("gateway")

    if not values["ingress"]["enabled"]:
        return

    k8s_config = pulumi.Config("kubernetes")

    stack = pulumi.get_stack()

    gateway_name = "{}-{}-gateway".format(stack, pulumi.get_project())

    gateway_metadata = {"labels": {"app": gateway_name, "release": stack}}

    spec = {"rules": []}

    for h in values["ingress"]["hosts"]:
        spec["rules"].append(
            {
                "host": h,
                "http": {
                    "paths": [
                        {
                            "path": values["ingress"]["path"],
                            "backend": {
                                "serviceName": gateway_name,
                                "servicePort": "http",
                            },
                        }
                    ]
                },
            }
        )

    if values["ingress"]["tls"]:
        spec["tls"] = []

        for t in values["ingress"]["tls"]:
            spec["tls"].append({"hosts": t["hosts"], "secretName": t["secretName"]})

    return Ingress(gateway_name, metadata=gateway_metadata, spec=spec)
