import pulumi
from pulumi_kubernetes.helm.v2 import Chart, ChartOpts, FetchOpts
from deepmerge import always_merger

default_chart_values = {
    "nameOverride": "gw-redis",
    "cluster": {"enabled": False},
    "usePassword": False,
    "networkPolicy": {"enabled": True, "allowExternal": False},
    "master": {
        "persistence": {"enabled": False},
        "resources": {"requests": {"cpu": "100m", "memory": "512Mi"}},
    },
}


def redis(global_config, chart_reqs):
    redis_config = pulumi.Config("redis")
    values = redis_config.get_object("values") or {}

    values = always_merger.merge(default_chart_values, values)

    global_config["redis"] = {"fullname": "{}-redis".format(pulumi.get_stack())}

    values["global"] = global_config["global"]

    chart_repo = chart_reqs.get("redis", "repository")
    if chart_repo.startswith("http"):
        repo = None
        fetchopts = FetchOpts(repo=chart_repo)
    else:
        repo = chart_repo
        fetchopts = None
    return Chart(
        global_config["redis"]["fullname"],
        config=ChartOpts(
            chart="redis",
            repo=repo,
            fetch_opts=fetchopts,
            version=chart_reqs.get("redis", "version"),
            values=values,
        ),
    )
