{{/* vim: set filetype=mustache: */}}
{{/*
Define clients and users for Keycloak
*/}}
{{- define "renku.keycloak.clients" -}}
[
  {
    "clientId": "renku",
    "baseUrl": "{{ template "http" . }}://{{ .Values.global.renku.domain }}",
    "secret": "{{ required "Fill in .Values.global.gateway.clientSecret with `uuidgen -r`" .Values.global.gateway.clientSecret }}",
    "redirectUris": [
        "{{ template "http" . }}://{{ .Values.global.renku.domain }}/*"
    ],
    "webOrigins": [
        "{{ template "http" . }}://{{ .Values.global.renku.domain }}/*"
    ],
    "protocolMappers": [{
      "name": "renku audience for renku",
      "protocol": "openid-connect",
      "protocolMapper": "oidc-audience-mapper",
      "consentRequired": false,
      "config": {
        "included.client.audience": "renku",
        "id.token.claim": false,
        "access.token.claim": true,
        "userinfo.token.claim": false
      }
    }]
  },
  {
    "clientId": "renku-cli",
    "baseUrl": "{{ template "http" . }}://{{ .Values.global.renku.domain }}",
    "secret": "{{ required "Fill in .Values.global.gateway.cliClientSecret with `uuidgen -r`" .Values.global.gateway.cliClientSecret }}",
    "redirectUris": [
        "{{ template "http" . }}://{{ .Values.global.renku.domain }}/*"
    ],
    "webOrigins": [
        "{{ template "http" . }}://{{ .Values.global.renku.domain }}/*"
    ],
    "protocolMappers": [{
      "name": "renku audience for renku cli",
      "protocol": "openid-connect",
      "protocolMapper": "oidc-audience-mapper",
      "consentRequired": false,
      "config": {
        "included.client.audience": "renku",
        "id.token.claim": false,
        "access.token.claim": true,
        "userinfo.token.claim": false
      }
    }]
  },
  {
    "clientId": "{{ .Values.notebooks.oidc.clientId }}",
    "baseUrl": "{{ template "http" . }}://{{ .Values.global.renku.domain }}",
    "secret": "{{ required "Fill in .Values.notebooks.oidc.clientSecret with `uuidgen -r`" .Values.notebooks.oidc.clientSecret }}",
    "redirectUris": [
        "{{ template "http" . }}://{{ .Values.global.renku.domain }}/*"
    ],
    "webOrigins": [
        "{{ template "http" . }}://{{ .Values.global.renku.domain }}/*"
    ],
    "protocolMappers": [{
      "name": "renku audience for renku",
      "protocol": "openid-connect",
      "protocolMapper": "oidc-audience-mapper",
      "consentRequired": false,
      "config": {
        "included.client.audience": "renku",
        "id.token.claim": false,
        "access.token.claim": true,
        "userinfo.token.claim": false
      }
    }]
  },
  {
    "clientId": "swagger",
    "publicClient": true,
    "baseUrl": "{{ template "http" . }}://{{ .Values.global.renku.domain }}",
    "redirectUris": [
        "{{ template "http" . }}://{{ .Values.global.renku.domain }}/*"
    ],
    "webOrigins": [
        "{{ template "http" . }}://{{ .Values.global.renku.domain }}/*"
    ],
    "attributes": {
        "pkce.code.challenge.method": "S256"
    },
    "protocolMappers": [{
      "name": "renku audience for the swagger UI",
      "protocol": "openid-connect",
      "protocolMapper": "oidc-audience-mapper",
      "consentRequired": false,
      "config": {
        "included.client.audience": "renku",
        "id.token.claim": false,
        "access.token.claim": true,
        "userinfo.token.claim": false
      }
    }]
  }

  {{- if .Values.gitlab.enabled -}}
  ,{
    "clientId": "gitlab",
    "baseUrl": "{{ template "http" . }}://{{ .Values.global.renku.domain }}/gitlab",
    "secret": "{{ required "Fill in .Values.global.gitlab.clientSecret with `uuidgen -r`" .Values.global.gitlab.clientSecret }}",
    "redirectUris": [
      "{{ template "http" . }}://{{ .Values.global.renku.domain }}/gitlab/users/auth/oauth2_generic/callback"
    ],
    "webOrigins": []
  }
  {{- end -}}
]
{{- end -}}

{{- define "renku.keycloak.users" -}}
[
  {{- if .Values.keycloak.createDemoUser -}}
  {
    "username": "demo@datascience.ch",
    "password": "{{ randAlphaNum 32 }}",
    "enabled": true,
    "emailVerified": true,
    "firstName": "John",
    "lastName": "Doe",
    "email": "demo@datascience.ch"
  }
  {{- end -}}
]
{{- end -}}
