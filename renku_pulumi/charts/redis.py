from .base_chart import BaseChart
import pulumi
from pulumi_kubernetes.helm.v2 import ChartOpts


def delete_before_replace_resources(obj, opts):
    """change some resources to be deleted before upgrade to fix deployment errors."""
    types = ["PodDisruptionBudget", "RoleBinding", "Role", "ServiceAccount", "NetworkPolicy"]

    if obj["kind"] in types:
        opts.delete_before_replace = True

class RedisChart(BaseChart):
    """Renku Redis chart."""

    name = "redis"
    default_values_template = {
        "nameOverride": "gw-redis",
        "cluster": {"enabled": False},
        "usePassword": False,
        "networkPolicy": {"enabled": True, "allowExternal": False},
        "master": {
            "persistence": {"enabled": False},
            "resources": {"requests": {"cpu": "100m", "memory": "512Mi"}},
        },
    }

    def __init__(self, config, global_config=None, dependencies=[]):
        global_config["redis"] = {"fullname": "{}-redis".format(pulumi.get_stack())}
        self.release_name = global_config["redis"]["fullname"]

        super().__init__(config, global_config=global_config, dependencies=dependencies)


    @property
    def chart_opts(self):
        """Get the Chart config."""
        return ChartOpts(
            chart=self.chart_name,
            version=self.chart_version,
            repo=self.chart_repo,
            fetch_opts=self.fetch_opts,
            values=self.values,
            transformations=[delete_before_replace_resources]
        )
