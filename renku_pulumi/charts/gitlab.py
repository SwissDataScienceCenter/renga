import pulumi
from pulumi_kubernetes.helm.v2 import Chart, ChartOpts, FetchOpts
from deepmerge import always_merger

default_chart_values = {
    "password": "gitlabadmin",
    "image": {"repository": "gitlab/gitlab-ce", "tag": "11.8.10-ce.0"},
    "oauth": {"autoSignIn": True},
    "demoUserIsAdmin": False,
    "persistence": {"size": "30Gi"},
    "registry": {"enabled": False},
}


def gitlab(config, global_config, chart_reqs):
    gitlab_config = pulumi.Config("gitlab")
    values = gitlab_config.get_object("values") or {}

    values = always_merger.merge(default_chart_values, values)

    values["global"] = global_config["global"]

    chart_repo = chart_reqs.get("gitlab", "repository")
    if chart_repo.startswith("http"):
        repo = None
        fetchopts = FetchOpts(repo=chart_repo)
    else:
        repo = chart_repo
        fetchopts = None

    return Chart(
        "{}-gitlab".format(pulumi.get_stack()),
        config=ChartOpts(
            chart="gitlab",
            repo=repo,
            fetch_opts=fetchopts,
            version=chart_reqs.get("gitlab", "version"),
            values=values,
        ),
    )
