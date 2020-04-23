import pulumi
from pulumi_random.random_id import RandomId

from charts import (
    renku_ui,
    renku_graph,
    renku_notebooks,
    postgresql,
    minio,
    keycloak,
    keycloak_secrets,
    gitlab,
    redis,
)

from resources.main import (
    configmap,
    ingress,
    postgres_postinstall_job,
    gitlab_postinstall_job,
    keycloak_postinstall_job,
    gitlab_secrets,
    graph_secrets,
    jupyterhub_secrets,
    renku_secret,
)

from resources import gateway
from deepmerge import always_merger

from configparser import ConfigParser

default_global_values = {
    "tests": {"image": {"repository": "renku/tests", "tag": "latest"}},
    "gateway": {},
    "graph": {
        "dbEventLog": {
            "postgresPassword": {"value": None, "overwriteOnHelmUpgrade": False},
            "existingSecret": None,
        },
        "tokenRepository": {
            "postgresPassword": {"value": None, "overwriteOnHelmUpgrade": False},
            "existingSecret": None,
        },
        "jena": {},
    },
    "renku": {},
    "useHTTPS": True,
}


def get_global_values(config):
    global_values = pulumi.Config("global")
    global_values = global_values.get_object("values") or {}

    stack = pulumi.get_stack()

    if config.get_bool("dev"):
        # set values for dev deployment
        default_global_values["gateway"]["clientSecret"] = RandomId(
            "gateway_client_secret", byte_length=32
        ).hex

        default_global_values["gateway"]["gitlabClientSecret"] = RandomId(
            "gateway_gitlab_client_secret", byte_length=32
        ).hex

        baseurl = config.get("baseurl")
        k8s_config = pulumi.Config("kubernetes")

        if baseurl:
            default_global_values["renku"]["domain"] = "{}.{}".format(
                k8s_config.require("namespace"), baseurl
            )

    default_global_values["graph"]["jena"]["dataset"] = stack

    global_values = always_merger.merge(default_global_values, global_values)

    return global_values


def deploy():
    config = pulumi.Config()

    chart_reqs = ConfigParser()
    chart_reqs.read("chart_requirements.ini")

    global_values = get_global_values(config)

    # global config is used to propagate dynamic values
    global_config = {}

    global_config["http"] = "https" if global_values["useHTTPS"] else "http"
    global_config["global"] = global_values

    if config.require_bool("gitlab_enabled"):
        gps, gss = gitlab_secrets()
        g = gitlab(config, global_config, chart_reqs)
        gitlab_postinstall_job(global_config, gps, [g, gss])

    renku_secret(global_config)

    # ui
    ui = renku_ui(config, global_config, chart_reqs)

    cfg_map = configmap(global_config)

    p = None
    pg_job = None
    graph = None
    kc_job = None

    pg, tok = graph_secrets()

    if config.require_bool("postgres_enabled"):
        p = postgresql(config, global_config, chart_reqs)

    if config.require_bool("graph_enabled"):
        graph = renku_graph(config, global_config, chart_reqs, pg, tok, p)

    pg_job = postgres_postinstall_job(global_config, pg, tok, cfg_map, [p])

    if config.require_bool("keycloak_enabled"):
        kp, ks, kus = keycloak_secrets(global_config)
        keycloak_chart = keycloak(config, global_config, chart_reqs, p, [pg_job])

    if config.require_bool("minio_enabled"):
        minio(config, global_config)

    gateway_values = gateway.gateway_values(global_config)

    js = jupyterhub_secrets()
    nb = renku_notebooks(
        config, global_config, chart_reqs, js, p, dependencies=[pg_job]
    )

    # gateway
    redis_chart = redis(global_config, chart_reqs)
    sc = gateway.secret(global_config, gateway_values)
    cfg = gateway.configmaps(global_config, gateway_values)
    gateway.ingress(global_config, gateway_values)
    gd = gateway.gateway_deployment(global_config, gateway_values, sc, cfg)
    gs = gateway.gateway_service(global_config, gateway_values, sc, cfg, gd)

    ing = ingress(global_config, dependencies=[gd, nb, ui, graph, keycloak_chart])
    gad = gateway.gateway_auth_deployment(
        global_config, gateway_values, sc, cfg, redis_chart, dependencies=[ing]
    )
    gas = gateway.gateway_auth_service(global_config, gateway_values, sc, cfg, gad)

    if config.require_bool("keycloak_enabled"):
        kc_job = keycloak_postinstall_job(
            global_config, kus, [keycloak_chart, kp, ks, ing]
        )


if __name__ == "__main__":
    deploy()
