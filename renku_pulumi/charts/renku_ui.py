import pulumi
from pulumi_kubernetes.helm.v2 import Chart, ChartOpts, FetchOpts
from deepmerge import always_merger

default_chart_values = {
    "ingress": {"enabled": False},
    "service": {"type": "ClusterIP", "port": 80},
    "welcomePage": {
        "text": "## Welcome to Renku!\nRenku is software for collaborative data science.\nWith Renku you can share code and data, discuss problems and solutions, and coordinate data-science projects.\n## Template\nI am templateable, so deployment specific information can be put here!\n"
    },
    "resources": {"requests": {"cpu": "100m", "memory": "128Mi"}},
    "templatesRepository": {
        "url": "https://github.com/SwissDataScienceCenter/renku-project-template",
        "ref": "master",
    },
}


def renku_ui(config, global_config, chart_reqs):
    ui_config = pulumi.Config("ui")
    values = ui_config.get_object("values") or {}

    if config.get_bool("dev"):
        k8s_config = pulumi.Config("kubernetes")

        baseurl = config.get("baseurl")

        if baseurl:
            default_chart_values["baseUrl"] = "https://{}.{}".format(
                k8s_config.require("namespace"), baseurl
            )
            default_chart_values["gitlabUrl"] = "https//{}/gitlab".format(baseurl)
            default_chart_values["gatewayUrl"] = "https://{}.{}/api".format(
                k8s_config.require("namespace"), baseurl
            )
            default_chart_values["jupyterhubUrl"] = "https://{}.{}/jupyterhub".format(
                k8s_config.require("namespace"), baseurl
            )

    values = always_merger.merge(default_chart_values, values)

    values["global"] = global_config["global"]

    global_config["ui"] = values

    chart_repo = chart_reqs.get("ui", "repository")
    if chart_repo.startswith("http"):
        repo = None
        fetchopts = FetchOpts(repo=chart_repo)
    else:
        repo = chart_repo
        fetchopts = None

    return Chart(
        "{}-ui".format(pulumi.get_stack()),
        config=ChartOpts(
            chart="renku-ui",
            version=chart_reqs.get("ui", "version"),
            repo=repo,
            fetch_opts=fetchopts,
            values=values,
        ),
    )
