.. _graph_services:

Graph services
==============

In Renku, the dependencies of research artifacts are recorded into a knowledge
graph. Each project's local knowledge graph is recorded in its repository; the
creation of the global knowledge graph is possible via the graph services. When
a project's repository is pushed to the server, a webhook is triggered that
causes the changes represented by the commits and all of the captured
dependencies to be rendered as RDF triples and pushed to the triple store.

The graph services are made up of four micro-services: the webhook-service,
triples-generator, token-repository and knowledge-graph. The knowledge graph data
is stored in the triple store (currently Apache Jena). The basic architecture is
illustrated below.

.. _fig-graph-services-architecture:

.. graphviz:: /_static/graphviz/graph_services_architecture.dot


Sequence diagram of Graph Services APIs and processes.
""""""""""""""""""""""""""""""""""""""""""""""""""""""
**POST <knowledge-graph>/knowledge-graph/graphql**

An endpoint that allows performing GraphQL queries on the Knowledge Graph data.

.. uml:: ../../_static/uml/knowledge-graph-graphql-sequence.uml

**POST <webhook-service>/projects/:id/webhooks**

An endpoint to create a Graph Services webhook for a project in GitLab.

.. uml:: ../../_static/uml/graph-create-hook-sequence.uml

**POST <webhook-service>/projects/:id/webhooks/validation**

An endpoint to validate project's webhook. It checks if a relevant
Graph Services webhook exists on the repository in GitLab and
if Graph Services have an Access Token associated with the project
so they can use it for finding project specific information in GitLab.

.. uml:: ../../_static/uml/graph-validate-hook-sequence.uml

**POST <webhook-service>/webhooks/events**

An endpoint to send Push Events containing information about commits pushed to the GitLab.

.. uml:: ../../_static/uml/graph-push-event-sequence.uml

**GET <webhook-service>/projects/:id/events/status**

An endpoint that returns information about processing progress of events for a specific project.

.. uml:: ../../_static/uml/graph-events-status-sequence.uml

**Subscription to unprocessed Commit Events**

A process initiated and maintained by Triples Generator instances
so Event Log can send them Events requiring generation of triples.

.. uml:: ../../_static/uml/graph-commit-events-subscription-sequence.uml

**Commit Events to RDF Triples**

A process responsible for translating unprocessed Commit Events from the Event Log
to RDF Triples in the RDF Store. This process runs continuously
by polling the Event Log for unprocessed Commit Events.

.. uml:: ../../_static/uml/graph-commit-event-sequence.uml

**Missed commits synchronization job**

A scheduled job which synchronizes state between the Event Log and GitLab
and generates Commit Events missing from the Event Log.
It runs periodically with a configured interval.

.. uml:: ../../_static/uml/graph-sync-events-sequence.uml


**Knowledge Graph re-provisioning process**

A process executed on Triples Generator start-up that checks if triples
in the RDF Store were generated with the version of renku-python currently set in the Triples Generator.

.. uml:: ../../_static/uml/graph-reprovisioning-sequence.uml
