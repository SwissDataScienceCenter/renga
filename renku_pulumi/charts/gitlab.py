import pulumi
from pulumi.resource import CustomTimeouts

from .base_chart import BaseChart


class GitlabChart(BaseChart):
    """Gitlab Chart."""

    name = "gitlab"
    default_values_template = {
        "password": "gitlabadmin",
        "oauth": {"autoSignIn": True},
        "demoUserIsAdmin": False,
    }

    def __init__(self, config, postgres_chart, gitlab_postgres_secret,
                 global_config=None, dependencies=[]):
        self.postgres_chart = postgres_chart
        self.gitlab_postgres_secret = gitlab_postgres_secret

        self.release_name = pulumi.get_stack()

        dependencies = [d for d in dependencies if d]

        super().__init__(
            config, global_config=global_config, dependencies=dependencies)

    @property
    def opts(self):
        return pulumi.ResourceOptions(
            depends_on=self.dependencies,
            custom_timeouts=CustomTimeouts(create="30m"))

    @property
    def default_values(self):
        """Get chart default values."""
        default_values = super().default_values
        if self.postgres_chart:
            default_values["postgresqlHost"] = self.delayed_chart_property(
                self.postgres_chart, lambda k, s: k.startswith("v1/Service"),
                "name")

        if self.gitlab_postgres_secret:
            default_values['postgresSecret'] = \
                self.gitlab_postgres_secret.metadata['name']

        return default_values

    def values_post_process(self, values):
        values = super().values_post_process(values)
