import pulumi
from pulumi_kubernetes.helm.v2 import Chart, ChartOpts, FetchOpts
from pulumi_random.random_id import RandomId

from deepmerge import Merger

default_chart_values = {
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


def renku_notebooks(
    config, global_config, chart_reqs, secret, postgres, dependencies=[]
):
    notebooks_config = pulumi.Config("notebooks")
    values = notebooks_config.get_object("values") or {}

    stack = pulumi.get_stack()

    chart_name = "{}-notebooks".format(stack)

    if config.get_bool("dev"):
        default_chart_values["jupyterhub"]["hub"]["cookieSecret"] = RandomId(
            "notebook_jupyterhub_cookie_secret", byte_length=32
        ).hex

        default_chart_values["jupyterhub"]["hub"]["services"]["notebooks"][
            "apiToken"
        ] = RandomId("notebook_jupyterhub_notebooks_api_token", byte_length=32).hex

        default_chart_values["jupyterhub"]["auth"]["state"]["cryptoKey"] = RandomId(
            "notebook_jupyterhub_auth_crypto_key", byte_length=32
        ).hex

        default_chart_values["jupyterhub"]["proxy"]["secretToken"] = RandomId(
            "notebook_jupyterhub_proxy_secret_token", byte_length=32
        ).hex

        baseurl = config.get("baseurl")
        k8s_config = pulumi.Config("kubernetes")

        if baseurl:
            default_chart_values["gitlab"]["registry"]["host"] = "registry.{}".format(
                baseurl
            )
            gitlab_url = "https://{}/gitlab".format(baseurl)
            default_chart_values["gitlab"]["url"] = gitlab_url
            default_chart_values["jupyterhub"]["hub"]["extraEnv"].append(
                {"name": "GITLAB_URL", "value": gitlab_url}
            )
            default_chart_values["jupyterhub"]["hub"]["services"]["gateway"][
                "oauth_redirect_uri"
            ] = "https://{}.{}/api/auth/jupyterhub/token".format(
                k8s_config.require("namespace"), baseurl
            )
            default_chart_values["jupyterhub"]["auth"]["gitlab"][
                "callbackUrl"
            ] = "https://{}.{}/jupyterhub/hub/oauth_callback".format(
                k8s_config.require("namespace"), baseurl
            )

        if postgres:
            default_chart_values["jupyterhub"]["hub"]["db"]["type"] = "postgres"
            default_chart_values["jupyterhub"]["hub"]["db"]["url"] = (
                postgres.get_resource(
                    "extensions/v1beta1/Deployment", "{}-postgresql".format(stack)
                )
                .metadata["name"]
                .apply(
                    lambda n: "postgres+psycopg2://jupyterhub@{}:5432/jupyterhub".format(
                        n
                    )
                )
            )

    if "gateway" in global_config:

        if (
            "jupyterhub" in global_config["gateway"]
            and "clientSecret" in global_config["gateway"]["jupyterhub"]
        ):
            default_chart_values["jupyterhub"]["hub"]["services"]["gateway"][
                "apiToken"
            ] = global_config["gateway"]["jupyterhub"]["clientSecret"]
    if "clientAppId" in global_config["global"]["gitlab"]:
        default_chart_values["jupyterhub"]["auth"]["gitlab"][
            "clientId"
        ] = global_config["global"]["gitlab"]["clientAppId"]
    if "clientAppSecret" in global_config["global"]["gitlab"]:
        default_chart_values["jupyterhub"]["auth"]["gitlab"][
            "clientSecret"
        ] = global_config["global"]["gitlab"]["clientAppSecret"]

    default_chart_values["jupyterhub"]["hub"]["extraEnv"].append(
        {
            "name": "PGPASSWORD",
            "valueFrom": {
                "secretKeyRef": {
                    "name": secret.metadata["name"],
                    "key": "jupyterhub-postgres-password",
                }
            },
        }
    )

    default_chart_values["jupyterhub"]["hub"]["services"]["notebooks"][
        "url"
    ] = "http://{}-renku-notebooks".format(chart_name)

    merger = Merger(
        [(list, [no_duplicate_list_merge]), (dict, ["merge"])],
        ["override"],
        ["override"],
    )

    values = merger.merge(default_chart_values, values)

    sentry = config.get("sentry_dsn")

    if sentry:
        hub = values.setdefault("jupyterhub", {})
        singleuser = hub.setdefault("singleuser", {})
        singleuser.setdefault("sentryDsn", sentry)

    dependencies.append(secret)
    dependencies.append(postgres)

    dependencies = [d for d in dependencies if d]

    values["global"] = global_config["global"]

    chart_repo = chart_reqs.get("notebooks", "repository")
    if chart_repo.startswith("http"):
        repo = None
        fetchopts = FetchOpts(repo=chart_repo)
    else:
        repo = chart_repo
        fetchopts = None
    return Chart(
        chart_name,
        config=ChartOpts(
            chart="renku-notebooks",
            version=chart_reqs.get("notebooks", "version"),
            repo=repo,
            fetch_opts=fetchopts,
            values=values,
            transformations=[delete_before_replace_resources],
        ),
        opts=pulumi.ResourceOptions(depends_on=dependencies),
    )
