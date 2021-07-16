.. _api_gateway:

API gateway
===========

The API gateway acts as a middle layer between the Renku clients and the
different backend services (GitLab, JupyterHub, Renku storage service, ...).
More specifically, the API gateway makes life easier for client developers in
the following ways:

- **Translation layer**:
  In cases where the data model used in the backend service
  does not match the data model of Renku, the gateway performs the necessary parsing
  of the resources and thus prevents re-implementation of very similar code throughout
  all clients.

- **Resource specific routing**:
  Notebook servers are stored in JupyterHub, project details in GitLab and datasets
  have to be fetched through the storage service - this must not be the worry of
  each client (developer), instead it is handled by the gateway.

- **Token handling**:
  Even with all backend services offering the possibility to rely on an OpenID-connect
  provider (OIDC) such as Keycloak, the API of those services do not currently accept
  access tokens issued by the OIDC providers. The gateway stores the access tokens
  for the different services, therefore allowing clients to access all resources
  using the same credentials.

- **Extensibility**:
  By adapting the mapping in the configuration file `endpoints.json`, it is possible to
  introduce other backend services, specifying the URL mapping,
  authentication/authorization scheme and content translation.
  Base classes for request/response processing and authentication headers can be extended
  and if needed, rounds of oauth2 login can be appended to the login workflow for
  retrieving user tokens.

- **Confidential client**:
  The gateway serves as the confidential part of the web UI, which is a single
  page application and can therefore not store client secrets. This allows
  using the `OAuth2 authorization code grant`__ for user login.

.. _grant: https://tools.ietf.org/html/rfc6749#page-8
__ grant_

The diagram below illustrates the sequence of events that currently take place
in the API gateway.

.. _fig-uml_gateway_service:

.. uml:: ../../_static/uml/gateway-sequence.uml
   :alt: Sequence diagram of notebook launch from the UI via the Notebooks Service.
