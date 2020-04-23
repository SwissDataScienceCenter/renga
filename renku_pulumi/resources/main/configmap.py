import pulumi
from pulumi_kubernetes.core.v1 import ConfigMap
from jinja2 import Template

# Unashamedly copied from: https://github.com/docker-library/postgres/blob/master/9.6/docker-entrypoint.sh
POSTGRES_INIT_SCRIPT = Template(
    """#!/bin/bash
set -ex
env

until sleep 1; pg_isready; do
    echo waiting for postgres
done

# It's ok if init scripts fail (databases already exist)
set +e
for f in /scripts/init-*-db*; do
    case "$f" in
    *.sh)
        # https://github.com/docker-library/postgres/issues/450#issuecomment-393167936
        # https://github.com/docker-library/postgres/pull/452
        if [ -x "$f" ]; then
        echo "$0: running $f"
        "$f"
        else
        echo "$0: sourcing $f"
        . "$f"
        fi
        ;;
    *.sql)    echo "$0: running $f"; "${psql[@]}" -f "$f"; echo ;;
    *.sql.gz) echo "$0: running $f"; gunzip -c "$f" | "${psql[@]}"; echo ;;
    *)        echo "$0: ignoring $f" ;;
    esac
    echo
done""",
    trim_blocks=True,
    lstrip_blocks=True,
)

JUPYTERHUB_INIT_SCRIPT = Template(
    """#!/bin/bash
set -x

JUPYTERHUB_POSTGRES_PASSWORD=$(cat /jupyterhub-postgres/jupyterhub-postgres-password)

psql -v ON_ERROR_STOP=1 <<-EOSQL
    create database "{{ global.jupyterhub.postgresDatabase }}";
    create user "{{ global.jupyterhub.postgresUser }}" password '$JUPYTERHUB_POSTGRES_PASSWORD';
EOSQL

psql -v ON_ERROR_STOP=1 --dbname "{{ global.jupyterhub.postgresDatabase }}" <<-EOSQL
    create extension if not exists "pg_trgm";
    revoke all on schema "public" from "public";
    grant all privileges on database "{{ global.jupyterhub.postgresDatabase }}" to "{{ global.jupyterhub.postgresUser }}";
    grant all privileges on schema "public" to "{{ global.jupyterhub.postgresUser }}";
EOSQL""",
    trim_blocks=True,
    lstrip_blocks=True,
)

GITLAB_INIT_SCRIPT = Template(
    """#!/usr/bin/env bash
set -ex
env

apt-get update -y
apt-get install -y curl jq

GITLAB_SERVICE_URL="http://{{ global.gitlab.fullname }}{{ global.gitlab.urlPrefix }}"
GITLAB_URL="{{ ui.gitlabUrl }}"

until sleep 1; curl -f -s --connect-timeout 5 ${GITLAB_SERVICE_URL}/help; do
    echo waiting for gitlab
done

psql -v ON_ERROR_STOP=1 <<-EOSQL
    DELETE FROM oauth_applications WHERE uid='jupyterhub';
    INSERT INTO oauth_applications (name, uid, scopes, redirect_uri, secret, trusted)
    VALUES ('jupyterhub', 'jupyterhub', 'api read_user', '{{ global.http }}://{{ global.renku.domain }}{{ notebooks.jupyterhub.hub.baseUrl }}hub/oauth_callback {{ global.http }}://{{ global.renku.domain }}/jupyterhub/hub/api/oauth2/authorize', '${JUPYTERHUB_AUTH_GITLAB_CLIENT_SECRET}', 'true');

    DELETE FROM oauth_applications WHERE uid='{{ global.gateway.gitlabClientId }}';
    INSERT INTO oauth_applications (name, uid, scopes, redirect_uri, secret, trusted)
    VALUES ('renku-ui', '{{ global.gateway.gitlabClientId }}', 'api read_user read_repository read_registry openid', '{{ global.http }}://{{ global.renku.domain }}/login/redirect/gitlab {{ global.http }}://{{ global.renku.domain }}/api/auth/gitlab/token', '${GATEWAY_GITLAB_CLIENT_SECRET}', 'true');
EOSQL
# configure the logout redirect
# curl -f -is -X PUT -H "Private-token: ${GITLAB_SUDO_TOKEN}" \
#   ${GITLAB_SERVICE_URL}/api/v4/application/settings?after_sign_out_path={{ global.http }}://{{ global.renku.domain }}/auth/realms/Renku/protocol/openid-connect/logout?redirect_uri={{ global.http }}://{{ global.renku.domain }}/api/auth/logout%3Fgitlab_logout=1""",
    trim_blocks=True,
    lstrip_blocks=True,
)

KEYCLOAK_INIT_SCRIPT = Template(
    """#!/bin/bash
set -x

KEYCLOAK_POSTGRES_PASSWORD=$(cat /keycloak-postgres/keycloak-postgres-password)

psql -v ON_ERROR_STOP=1 <<-EOSQL
    create database "{{ global.keycloak.postgresDatabase }}";
    create user "{{ global.keycloak.postgresUser }}" password '$KEYCLOAK_POSTGRES_PASSWORD';
EOSQL

psql -v ON_ERROR_STOP=1 --dbname "{{ global.keycloak.postgresDatabase }}" <<-EOSQL
    revoke all on schema "public" from "public";
    grant all privileges on database "{{ global.keycloak.postgresDatabase }}" to "{{ global.keycloak.postgresUser }}";
    grant all privileges on schema "public" to "{{ global.keycloak.postgresUser }}";
EOSQL""",
    trim_blocks=True,
    lstrip_blocks=True,
)

GITLAB_DB_INIT_SCRIPT = Template(
    """#!/bin/bash
set -x

GITLAB_POSTGRES_PASSWORD=$(cat /gitlab-postgres/gitlab-postgres-password)

psql -v ON_ERROR_STOP=1 <<-EOSQL
    create database "{{ global.gitlab.postgresDatabase }}";
    create user "{{ global.gitlab.postgresUser }}" password '$GITLAB_POSTGRES_PASSWORD';
EOSQL

psql -v ON_ERROR_STOP=1 --dbname "{{ global.gitlab.postgresDatabase }}" <<-EOSQL
    create extension if not exists "pg_trgm";
    revoke all on schema "public" from "public";
    grant all privileges on database "{{ global.gitlab.postgresDatabase }}" to "{{ global.gitlab.postgresUser }}";
    grant all privileges on schema "public" to "{{ global.gitlab.postgresUser }}";
EOSQL""",
    trim_blocks=True,
    lstrip_blocks=True,
)

GRAPH_EVENTLOG_INIT_SCRIPT = Template(
    """#!/bin/bash
set -x

DB_EVENT_LOG_POSTGRES_PASSWORD=$(cat /graph-db-postgres/graph-dbEventLog-postgresPassword)
DB_EVENT_LOG_DB_NAME=event_log

psql -v ON_ERROR_STOP=1 <<-EOSQL
create database "$DB_EVENT_LOG_DB_NAME";
create user "{{ global.graph.dbEventLog.postgresUser }}" password '$DB_EVENT_LOG_POSTGRES_PASSWORD';
EOSQL

psql postgres -v ON_ERROR_STOP=1 --dbname "$DB_EVENT_LOG_DB_NAME" <<-EOSQL
create extension if not exists "pg_trgm";
revoke all on schema "public" from "public";
grant all privileges on database "$DB_EVENT_LOG_DB_NAME" to "{{ global.graph.dbEventLog.postgresUser }}";
grant all privileges on schema "public" to "{{ global.graph.dbEventLog.postgresUser }}";
EOSQL""",
    trim_blocks=True,
    lstrip_blocks=True,
)

GRAPH_TOKENREPO_INIT_SCRIPT = Template(
    """#!/bin/bash
set -x

TOKEN_REPOSITORY_POSTGRES_PASSWORD=$(cat /graph-token-postgres/graph-tokenRepository-postgresPassword)
TOKEN_REPOSITORY_DB_NAME=projects_tokens

psql -v ON_ERROR_STOP=1 <<-EOSQL
create database "$TOKEN_REPOSITORY_DB_NAME";
create user "{{ global.graph.tokenRepository.postgresUser }}" password '$TOKEN_REPOSITORY_POSTGRES_PASSWORD';
EOSQL

psql postgres -v ON_ERROR_STOP=1 --dbname "$TOKEN_REPOSITORY_DB_NAME" <<-EOSQL
create extension if not exists "pg_trgm";
revoke all on schema "public" from "public";
grant all privileges on database "$TOKEN_REPOSITORY_DB_NAME" to "{{ global.graph.tokenRepository.postgresUser }}";
grant all privileges on schema "public" to "{{ global.graph.tokenRepository.postgresUser }}";
EOSQL""",
    trim_blocks=True,
    lstrip_blocks=True,
)


def configmap(global_config):
    config = pulumi.Config()

    ui_values = global_config["ui"]

    k8s_config = pulumi.Config("kubernetes")

    stack = pulumi.get_stack()

    template_values = {
        "global": {**global_config["global"], **global_config},
        "ui": ui_values,
    }

    data = {
        "init-postgres.sh": POSTGRES_INIT_SCRIPT.render(**template_values),
        "init-jupyterhub-db.sh": JUPYTERHUB_INIT_SCRIPT.render(**template_values),
    }
    gitlab_enabled = config.get_bool("gitlab_enabled")
    if gitlab_enabled:
        data["init-gitlab-db.sh"] = GITLAB_DB_INIT_SCRIPT.render(**template_values)
        if "sudoToken" in global_config["global"]["gitlab"]:
            data["init-gitlab.sh"] = GITLAB_INIT_SCRIPT.render(**template_values)

    if config.get_bool("keycloak_enabled"):
        data["init-keycloak-db.sh"] = KEYCLOAK_INIT_SCRIPT.render(**template_values)

    if config.get_bool("graph_enabled"):
        data["init-dbEventLog-db.sh"] = GRAPH_EVENTLOG_INIT_SCRIPT.render(
            **template_values
        )
        data["init-tokenRepository-db.sh"] = GRAPH_TOKENREPO_INIT_SCRIPT.render(
            **template_values
        )

    return ConfigMap(
        "{}-{}".format(stack, pulumi.get_project()),
        metadata={"labels": {"app": pulumi.get_project(), "release": stack}},
        data=data,
    )
