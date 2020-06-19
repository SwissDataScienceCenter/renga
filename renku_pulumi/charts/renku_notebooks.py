from .base_chart import BaseChart
import pulumi
from deepmerge.merger import Merger
from pulumi_kubernetes.helm.v2 import ChartOpts


def no_duplicate_list_merge(config, path, base, nxt):
    """Custom merge strategy for lists, only merge values that aren't present."""
    for i in base:
        if i in nxt:
            continue

        nxt.insert(0, i)

    return nxt


def delete_before_replace_resources(obj, opts):
    """change some resources to be deleted before upgrade to fix deployment errors."""
    types = ["PodDisruptionBudget", "RoleBinding", "Role", "ServiceAccount"]

    if obj["kind"] in types:
        opts.delete_before_replace = True


class NotebooksChart(BaseChart):
    """Renku notebooks chart."""

    name = "notebooks"
    chart_name = "renku-notebooks"
    default_values_template = {
        "gitlab": {"registry": {}},
        "securityContext": {"enabled": False},
        "resources": {"requests": {"cpu": "100m", "memory": "512Mi"}},
        "serverOptions": {
            "defaultUrl": {
                "order": 1,
                "displayName": "Default Environment",
                "type": "enum",
                "default": "/lab",
                "options": ["/lab", "/rstudio"],
            },
            "cpu_request": {
                "order": 2,
                "displayName": "Number of CPUs",
                "type": "enum",
                "default": 0.1,
                "options": [0.1, 0.5],
            },
            "mem_request": {
                "order": 3,
                "displayName": "Amount of Memory",
                "type": "enum",
                "default": "1G",
                "options": ["1G", "2G"],
            },
            "gpu_request": {
                "order": 4,
                "displayName": "Number of GPUs",
                "type": "enum",
                "default": 0,
                "options": [0],
            },
            "lfs_auto_fetch": {
                "order": 5,
                "displayName": "Automatically fetch LFS data",
                "type": "boolean",
                "default": False,
            },
        },
        "jupyterhub": {
            "hub": {
                "baseUrl": "/jupyterhub/",
                "allowNamedServers": True,
                "services": {
                    "notebooks": {},
                    "gateway": {"admin": True, "oauth_client_id": "gateway"},
                },
                "db": {},
                "extraEnv": [
                    {"name": "DEBUG", "value": "1"},
                    {
                        "name": "JUPYTERHUB_SPAWNER_CLASS",
                        "value": "spawners.RenkuKubeSpawner",
                    },
                ],
                "resources": {"requests": {"cpu": "200m", "memory": "512Mi"}},
            },
            "auth": {"state": {}, "gitlab": {}},
            "rbac": {"enabled": True},
            "scheduling": {
                "userPlaceholder": {"enabled": False},
                "userPods": {"nodeAffinity": {"matchNodePurpose": "require"}},
                "userScheduler": {"pdb": {"enabled": False}},
            },
            "singleuser": {
                "image": {"name": "renku/singleuser", "tag": "0.3.7-renku0.5.2"}
            },
            "proxy": {
                "service": {"type": "ClusterIP"},
                "https": {"enabled": False},
                "chp": {"resources": {"requests": {"cpu": "100m", "memory": "512Mi"}}},
            },
        },
    }

    def __init__(self, config, postgres_chart, jupyterhub_secret, global_config=None, dependencies=[]):
        self.postgres_chart = postgres_chart
        self.jupyterhub_secret = jupyterhub_secret

        dependencies.append(postgres_chart)
        dependencies.append(jupyterhub_secret)

        super().__init__(config, global_config=global_config, dependencies=dependencies)

    @property
    def default_values(self):
        default_values = super().default_values

        config = pulumi.Config()

        if config.get_bool("dev"):
            default_values["jupyterhub"]["hub"]["cookieSecret"] = \
                self.generate_random_id("notebook_jupyterhub_cookie_secret", 32)

            default_values["jupyterhub"]["hub"]["services"]["notebooks"][
                "apiToken"
            ] = self.generate_random_id("notebook_jupyterhub_notebooks_api_token", 32)

            default_values["jupyterhub"]["auth"]["state"]["cryptoKey"] = \
                self.generate_random_id("notebook_jupyterhub_auth_crypto_key", 32)

            default_values["jupyterhub"]["proxy"]["secretToken"] = \
                self.generate_random_id("notebook_jupyterhub_proxy_secret_token", 32)

            baseurl = config.get("baseurl")
            k8s_config = pulumi.Config("kubernetes")

            if baseurl:
                default_values["gitlab"]["registry"]["host"] = "registry.{}".format(
                    baseurl
                )
                gitlab_url = "https://{}/gitlab".format(baseurl)
                default_values["gitlab"]["url"] = gitlab_url
                default_values["jupyterhub"]["hub"]["extraEnv"].append(
                    {"name": "GITLAB_URL", "value": gitlab_url}
                )
                default_values["jupyterhub"]["hub"]["services"]["gateway"][
                    "oauth_redirect_uri"
                ] = "https://{}.{}/api/auth/jupyterhub/token".format(
                    k8s_config.require("namespace"), baseurl
                )
                default_values["jupyterhub"]["auth"]["gitlab"][
                    "callbackUrl"
                ] = "https://{}.{}/jupyterhub/hub/oauth_callback".format(
                    k8s_config.require("namespace"), baseurl
                )

            if self.postgres_chart:
                default_values["jupyterhub"]["hub"]["db"]["type"] = "postgres"
                default_values["jupyterhub"]["hub"]["db"]["url"] = self.delayed_chart_property(
                    self.postgres_chart,
                    lambda k, s: k.startswith("extensions/v1beta1/Deployment"),
                    "name"
                ).apply(
                        lambda n: "postgres+psycopg2://jupyterhub@{}:5432/jupyterhub".format(
                            n
                        )
                    )

        if "gateway" in self.global_config:
            if (
                "jupyterhub" in self.global_config["gateway"]
                and "clientSecret" in self.global_config["gateway"]["jupyterhub"]
            ):
                default_values["jupyterhub"]["hub"]["services"]["gateway"][
                    "apiToken"
                ] = self.global_config["gateway"]["jupyterhub"]["clientSecret"]
        if "clientAppId" in self.global_config["global"]["gitlab"]:
            default_values["jupyterhub"]["auth"]["gitlab"][
                "clientId"
            ] = self.global_config["global"]["gitlab"]["clientAppId"]
        if "clientAppSecret" in self.global_config["global"]["gitlab"]:
            default_values["jupyterhub"]["auth"]["gitlab"][
                "clientSecret"
            ] = self.global_config["global"]["gitlab"]["clientAppSecret"]

        default_values["jupyterhub"]["hub"]["extraEnv"].append(
            {
                "name": "PGPASSWORD",
                "valueFrom": {
                    "secretKeyRef": {
                        "name": self.jupyterhub_secret.metadata["name"],
                        "key": "jupyterhub-postgres-password",
                    }
                },
            }
        )

        default_values["jupyterhub"]["hub"]["services"]["notebooks"][
            "url"
        ] = "http://{}-renku-notebooks".format(self.release_name)

        return default_values

    @property
    def values(self):
        """Get chart values."""
        chart_config = self.pulumi_config
        values = chart_config.get_object("values") or {}

        merger = Merger(
            [(list, [no_duplicate_list_merge]), (dict, ["merge"])],
            ["override"],
            ["override"],
        )

        values = merger.merge(self.default_values, values)

        values = self.values_post_process(values)

        values["global"] = self.global_config["global"]
        self.global_config[self.name] = values

        return values

    def values_post_process(self, values):
        config = pulumi.Config()
        sentry = config.get("sentry_dsn")
        if sentry:
            hub = values.setdefault("jupyterhub", {})
            singleuser = hub.setdefault("singleuser", {})
            singleuser.setdefault("sentryDsn", sentry)

        return values


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
