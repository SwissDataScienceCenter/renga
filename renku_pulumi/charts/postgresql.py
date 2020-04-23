import pulumi
from pulumi_kubernetes.helm.v2 import Chart, ChartOpts, FetchOpts
from deepmerge import always_merger

default_chart_values = {
    "image": "postgres",
    "imageTag": "9.6",
    "postgresUser": "postgres",
    "postgresPassword": "postgres",
    "postgresDatabase": "postgres",
    "persistence": {
        "enabled": False,
        "accessMode": "ReadWriteOnce",
        "size": "8Gi",
        "subPath": "postgresql-db",
        "mountPath": "/var/lib/postgresql/data/pgdata",
    },
    "metrics": {
        "enabled": False,
        "image": "wrouesnel/postgres_exporter",
        "imageTag": "v0.1.1",
        "imagePullPolicy": "IfNotPresent",
        "resources": {"requests": {"memory": "256Mi", "cpu": "100m"}},
    },
    "resources": {"requests": {"cpu": "100m", "memory": "256Mi"}},
    "service": {"type": "ClusterIP", "port": 5432, "externalIPs": []},
    "networkPolicy": {"enabled": False, "allowExternal": True},
    "nodeSelector": {},
    "tolerations": [],
    "affinity": {},
    "probes": {
        "liveness": {"initialDelay": 60, "timeoutSeconds": 5, "failureThreshold": 6},
        "readiness": {"initialDelay": 5, "timeoutSeconds": 3, "periodSeconds": 5},
    },
    "deploymentAnnotations": {},
    "podAnnotations": {},
}


def postgresql(config, global_config, chart_reqs):
    postgres_config = pulumi.Config("postgres")
    values = postgres_config.get_object("values") or {}

    values = always_merger.merge(default_chart_values, values)

    global_config["postgres"] = values

    values["global"] = global_config["global"]

    chart_repo = chart_reqs.get("postgres", "repository")
    if chart_repo.startswith("http"):
        repo = None
        fetchopts = FetchOpts(repo=chart_repo)
    else:
        repo = chart_repo
        fetchopts = None
    return Chart(
        "{}-postgresql".format(pulumi.get_stack()),
        config=ChartOpts(
            chart="postgresql",
            repo=repo,
            fetch_opts=fetchopts,
            version=chart_reqs.get("postgres", "version"),
            values=values,
        ),
    )
