import pulumi
from pulumi_kubernetes.helm.v2 import Chart, ChartOpts, FetchOpts
from deepmerge import always_merger

default_chart_values = {}


def minio(config, global_config, chart_reqs):
    minio_config = pulumi.Config("minio")
    values = minio_config.get_object("values") or {}

    values = always_merger.merge(default_chart_values, values)

    values["global"] = global_config["global"]

    chart_repo = chart_reqs.get("minio", "repository")
    if chart_repo.startswith("http"):
        repo = None
        fetchopts = FetchOpts(repo=chart_repo)
    else:
        repo = chart_repo
        fetchopts = None
    return Chart(
        "{}-minio".format(pulumi.get_stack()),
        config=ChartOpts(
            chart="minio",
            repo=repo,
            fetch_opts=fetchopts,
            version=chart_reqs.get("minio", "version"),
            values=values,
        ),
    )
