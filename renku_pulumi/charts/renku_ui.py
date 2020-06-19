import pulumi
from .base_chart import BaseChart


class UIChart(BaseChart):
    """Renku notebooks chart."""

    name = "ui"
    chart_name = "renku-ui"
    default_values_template = {
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

    @property
    def default_values(self):
        default_values = super().default_values

        config = pulumi.Config()

        if config.get_bool("dev"):
            k8s_config = pulumi.Config("kubernetes")

            baseurl = config.get("baseurl")

            if baseurl:
                default_values["baseUrl"] = "https://{}.{}".format(
                    k8s_config.require("namespace"), baseurl
                )
                default_values["gitlabUrl"] = "https//{}/gitlab".format(baseurl)
                default_values["gatewayUrl"] = "https://{}.{}/api".format(
                    k8s_config.require("namespace"), baseurl
                )
                default_values["jupyterhubUrl"] = "https://{}.{}/jupyterhub".format(
                    k8s_config.require("namespace"), baseurl
                )

        return default_values
