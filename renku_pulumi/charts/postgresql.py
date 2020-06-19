from .base_chart import BaseChart


class PostgresChart(BaseChart):
    """Renku Postgres chart."""

    name = "postgres"
    chart_name = "postgresql"
    default_values_template = {
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
