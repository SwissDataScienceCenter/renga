from .base_chart import BaseChart
import pulumi


class GraphChart(BaseChart):
    """Renku Graph chart."""
    name = "graph"
    chart_name = "renku-graph"
    default_values_template = {
        "jena": {
            "users": {"admin": {}, "renku": {}},
            "resources": {"requests": {"cpu": "200m", "memory": "1Gi"}},
            "persistence": {"storageClass": "temporary"},
        },
        "gitlab": {},
        "webhookService": {
            "hookToken": {},
            "eventsSynchronization": {
                "initialDelay": "2 minutes", "interval": "1 hour"},
        },
        "tokenRepository": {"tokenEncryption": {}},
        "resources": {"requests": {"cpu": "100m", "memory": "2Gi"}},
    }

    def __init__(self, config, postgres_secret, token_secret, postgres_chart,
                 global_config=None, dependencies=[]):
        self.postgres_secret = postgres_secret
        self.token_secret = token_secret
        self.postgres_chart = postgres_chart

        dependencies = [self.postgres_secret, self.token_secret] + dependencies

        if postgres_chart:
            dependencies.append(self.postgres_chart)

        dependencies = [d for d in dependencies if d]

        super().__init__(
            config, global_config=global_config, dependencies=dependencies)

    @property
    def default_values(self):
        """Get chart default values."""
        default_values = super().default_values

        config = pulumi.Config()

        if config.get_bool("dev"):
            default_values["jena"]["users"]["admin"]["password"] = \
                self.generate_random_password("graph_jena_admin_password", 8)

            default_values["jena"]["users"]["renku"]["password"] = \
                self.generate_random_password("graph_jena_renku_password", 8)

            default_values["webhookService"]["hookToken"]["secret"] = \
                self.generate_random_id("graph_webhookservice_secret")

            default_values["tokenRepository"]["tokenEncryption"]["secret"] = \
                self.generate_random_id("graph_tokenrepository_secret")

            baseurl = config.get("baseurl")

            if baseurl:
                default_values["gitlab"]["url"] = "https://{}/gitlab".format(
                    baseurl)

        return default_values

    def values_post_process(self, values):
        values = super().values_post_process(values)

        values["global"] = self.global_config["global"]

        config = pulumi.Config()

        sentry = config.get("sentry_dsn")

        if sentry:
            sent = values.setdefault("sentry", {})
            sent.setdefault("sentryDsnRenkuPython", sentry)

        if self.postgres_chart and "postgresqlHost" not in values:
            values["postgresqlHost"] = self.postgres_chart.resources.apply(
                lambda r: next(s for k, s in r.items()
                               if k.startswith("v1/Service"))
            ).metadata["name"]

        values["global"]["graph"]["dbEventLog"][
            "existingSecret"
        ] = self.postgres_secret.metadata["name"]
        values["global"]["graph"]["tokenRepository"][
            "existingSecret"
        ] = self.token_secret.metadata["name"]

        return values
