- Install Pulumi: curl -fsSL https://get.pulumi.com | sh

- Checkout the pulumi PR: https://github.com/SwissDataScienceCenter/renku/pull/733

- Go into the `renku_pulumi/` subfolder

- Create a python environment and install the `requirements.txt` (`pip install -r requirements.txt`)

- Login to pulumi locally (this tells it where to store stack information): `pulumi login --local`

- Create a new pulumi stack (stack name should be same as kubernetes namespace): `pulumi stack init <stack_name>`

- The last step created the stack config file, `Pulumi.<stack_name>.yaml`, edit this file and add the following after the encryptionsalt line:

```
config:
  graph:values:
    sentry:
      enabled: true
      url: https://8b86fc8068ff4ff792f717f2cce02d16@sentry.dev.renku.ch/3
      environmentName:
  #keycloak:values:
  #ui:values:
  notebooks:values:
    sentryDsn: https://3420161bbeb64acf87de9fe26c363e6f@sentry.dev.renku.ch/4
    jupyterhub:
      auth:
        state:
          enabled: true
        type: gitlab
  gateway:values:
    jupyterhub:
      clientId: gateway
  #minio:values:
  #gitlab:values:
  #postgres:values:
  #redis:values:
  global:values:
    gitlab:
      postgresDatabase: gitlabhq_production
      postgresUser: gitlab
      urlPrefix: /gitlab
      clientAppId:
      clientAppSecret:
    keycloak:
      postgresDatabase: keycloak
      postgresUser: keycloak
    jupyterhub:
      postgresDatabase: jupyterhub
      postgresUser: jupyterhub
    gateway:
      gitlabClientId: renku-ui
    renku:
      version: 0.4.0
    graph:
      dbEventLog:
        ## Name of the postgres user to be used to access the Event Log db
        postgresUser: eventlog
      tokenRepository:
        ## Name of the postgres user to be used to access the db storing access tokens
        postgresUser: tokenstorage
        ## Postgres password to be used to access the db storing access tokens
    useHTTPS: true
  ingress:enabled: true
  ingress:annotations:
    kubernetes.io/ingress.class: nginx
    kubernetes.io/tls-acme: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: '0'
    nginx.ingress.kubernetes.io/proxy-request-buffering: 'off'
  #ingress:hosts:
  #ingress:tls:
  renku:sentry_dsn: https://579865fda8f2424ea29e19d1ab45e92b@sentry.dev.renku.ch/2
  renku:gitlab_enabled: "false"
  renku:graph_enabled: "true"
  renku:keycloak_enabled: "true"
  renku:minio_enabled: "false"
  renku:postgres_enabled: "true"
  renku:dev: "true"
  renku:baseurl: dev.renku.ch
  kubernetes:namespace:
```

- Fill in the kubernetes namespace in the `kubernetes:namespace:` and `graph:values: sentry: environmentName:` fields, as well as adding the gitlab application
  token id and secret in `global:values: gitlab: clientAppId:` and `global:values: gitlab: clientAppSecret:`.
  with the `global:  gitlab:    clientSecret:` value from your previous deployment yaml

- set the kubectl context to one approriate for the namespace you wish to deploy to (`kubectl config set-context <context>`)

- In the cmdline with the previously created python env active, run `pulumi up`. It should show you a preview of what is to be deployed, you can confirm/reject the changes or view a detailed diff
