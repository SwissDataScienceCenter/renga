import pulumi
from pulumi_kubernetes.core.v1 import ConfigMap
from jinja2 import Template

from .values import gateway_values

TRAEFIK_TEMPLATE = Template(
    """
{% if development %}
[Global]
  debug = true

[log]
  level = "debug"
{% else %}
[log]
  level = "error"
{% endif %}

[api]
  dashboard = true

[providers]
  [providers.file]
    directory = "/config"
    filename = "rules.toml"

[entrypoints]
  [entrypoints.http]
    address = ":{{ service.port }}"

[accessLog]
  bufferingSize = 10""",
    trim_blocks=True,
    lstrip_blocks=True,
)

RULES_TEMPLATE = Template(
    """
[http]
  [http.routers]
    [http.routers.gateway]
      entryPoints = ["http"]
      Rule = "PathPrefix(`{{ servicePrefix | default("/api/") }}auth`)"
      Service = "gateway"

    [http.routers.jupyterhub]
      entryPoints = ["http"]
      Middlewares = ["auth-jupyterhub", "common", "jupyterhub" ]
      Rule = "PathPrefix(`{{ servicePrefix | default("/api/") }}jupyterhub`)"
      Service = "jupyterhub"

    [http.routers.notebooks]
      entryPoints = ["http"]
      Middlewares = ["auth-jupyterhub", "common", "notebooks"]
      Rule = "PathPrefix(`{{ servicePrefix | default("/api/") }}notebooks`)"
      Service = "jupyterhub"

    [http.routers.webhooks]
      entryPoints = ["http"]
      Middlewares = ["auth-gitlab", "common", "webhooks"]
      Rule = "Path(`{{ servicePrefix | default("/api/") }}projects/{project-id}/graph/webhooks{endpoint:(.*)}`)"
      Service = "webhooks"

    [http.routers.graphstatus]
      entryPoints = ["http"]
      Middlewares = ["auth-gitlab", "common", "graphstatus"]
      Rule = "Path(`{{ servicePrefix | default("/api/") }}projects/{project-id}/graph/status{endpoint:(.*)}`)"
      Service = "webhooks"

    [http.routers.graphql]
      entryPoints = ["http"]
      Middlewares = ["common", "graphql"]
      Rule = "PathPrefix(`{{ servicePrefix | default("/api/") }}graphql`)"
      Service = "graphql"

    [http.routers.gitlab]
      entryPoints = ["http"]
      Middlewares = ["auth-gitlab", "common", "gitlab"]
      Rule = "PathPrefix(`{{ servicePrefix | default("/api/") }}`)"
      Service = "gitlab"

  [http.middlewares]
    [http.middlewares.common.chain]
      {% if development %}
      middlewares = ["general-ratelimit", "api", "noCookies", "development"]
      {% else %}
      middlewares = ["general-ratelimit", "api", "noCookies"]
      {% endif %}

    [http.middlewares.noCookies.headers]
      [http.middlewares.noCookies.headers.CustomRequestHeaders]
        Cookie = ""

    [http.middlewares.api.StripPrefix]
      prefixes = ["/api"]

    [http.middlewares.development.headers]
      isDevelopment = true

    [http.middlewares.gitlab.AddPrefix]
      prefix = "{{ global.gitlab.urlPrefix }}/api/v4"

    [http.middlewares.jupyterhub.ReplacePathRegex]
      regex = "^/jupyterhub/(.*)"
      replacement = "/jupyterhub/hub/api/$1"

    [http.middlewares.notebooks.ReplacePathRegex]
      regex = "^/notebooks/(.*)"
      replacement = "/jupyterhub/services/notebooks/$1"

    [http.middlewares.auth-gitlab.forwardauth]
      address = "http://{{ fullname }}-auth/?auth=gitlab"
      trustForwardHeader = true
      authResponseHeaders = ["Authorization"]

    [http.middlewares.auth-jupyterhub.forwardauth]
      address = "http://{{ fullname }}-auth/?auth=jupyterhub"
      trustForwardHeader = true
      authResponseHeaders = ["Authorization"]

    [http.middlewares.webhooks.ReplacePathRegex]
      regex = "^/projects/([^/]*)/graph/webhooks(.*)"
      replacement = "/projects/$1/webhooks$2"

    [http.middlewares.graphstatus.ReplacePathRegex]
      regex = "^/projects/([^/]*)/graph(.*)"
      replacement = "/projects/$1/events$2"

    [http.middlewares.graphql.ReplacePathRegex]
      regex = "/graphql"
      replacement = "/knowledge-graph/graphql"

    [http.middlewares.general-ratelimit.ratelimit]
      extractorfunc = "{{ rateLimits.general.extractorfunc }}"
      [http.middlewares.general-ratelimit.ratelimit.rateset.rate0]
        period = "{{ rateLimits.general.period }}"
        average = {{ rateLimits.general.average }}
        burst = {{ rateLimits.general.burst }}

  [http.services]
    [http.services.gateway.LoadBalancer]
      method = "drr"
      [[http.services.gateway.LoadBalancer.servers]]
        url = "http://{{ fullname }}-auth/"
        weight = 1

    [http.services.gitlab.LoadBalancer]
      method = "drr"
      [[http.services.gitlab.LoadBalancer.servers]]
        url = "{{ gitlabUrl | default("{}://{}/gitlab".format(global['http'], global['renku']['domain']) ) }}"
        weight = 1

    [http.services.jupyterhub.LoadBalancer]
      method = "drr"
      [[http.services.jupyterhub.LoadBalancer.servers]]
        url = "{{ jupyterhub.url | default("{}://{}/jupyterhub".format(global['http'], global['renku']['domain']) ) }}"
        weight = 1

    [http.services.webhooks.LoadBalancer]
      method = "drr"
      [[http.services.webhooks.LoadBalancer.servers]]
        url = "{{ graph.webhookService.hostname | default("http://{}-graph-webhook-service".format(release_name) )  }}"
        weight = 1

    [http.services.graphql.LoadBalancer]
      method = "drr"
      [[http.services.graphql.LoadBalancer.servers]]
      url = "{{ global.graph.fullname | default("%s{0}-knowledge-graph".format(release_name)) | format(global.graph.fullname) }}"
        weight = 1""",
    trim_blocks=True,
    lstrip_blocks=True,
)


def configmaps(global_config, values):
    config = pulumi.Config("gateway")

    k8s_config = pulumi.Config("kubernetes")

    stack = pulumi.get_stack()

    gateway_name = "{}-{}-gateway".format(stack, pulumi.get_project())

    gateway_metadata = {"labels": {"app": gateway_name, "release": stack}}

    template_values = {
        "release_name": stack,
        "fullname": gateway_name,
        "global": {**global_config["global"], **global_config},
        **values,
    }

    return ConfigMap(
        gateway_name,
        metadata=gateway_metadata,
        data={
            "traefik.toml": TRAEFIK_TEMPLATE.render(template_values),
            "rules.toml": RULES_TEMPLATE.render(template_values),
        },
    )
