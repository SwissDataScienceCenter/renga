.. _api_guidelines:


Renku REST API guidelines
=========================

This page describes a set of rules and recommendations that a developer of
any **Renku** related web service should follow when developing new or
refactoring existing code.

.. note::

   This is not a formal specification.

0. First steps
--------------

Make sure that your data model has started to stabilize. Focus on consistent
and concrete naming of your *resources* and possible relations between them.


1. Specification and Best Practices
-----------------------------------

The focus is on finding a right balance between standards and pragmatic API
design which should serve its purpose.

- `JSON API Specification`_ - a specification for building APIs in JSON
- `Pragmatic RESTful API`_ - blog post on best practices for designing
  a pragmatic RESTful API

.. _`JSON API Specification`: http://jsonapi.org/format/
.. _`Pragmatic RESTful API`: http://www.vinaysahni.com/best-practices-for-a-pragmatic-restful-api

There are some key principles that the developer of an API should aim for.

2. HTTP verbs
-------------

Most of the *resources* should support the four basic functions of `CRUD`_:

**Create**

    ``POST`` method **should** be used when a request is non-idempotent (for
    example a new resource is added to a database).

**Read**

    ``GET`` method **should not** change the state of the object itself. Side
    effects are possible for endpoints that require authorization only, but in
    any case these side effects should only create new objects used for
    capturing the resource lineage.

**Update**

    ``PUT`` method should be used to replace a full state of an existing
    object. To avoid `lost update <https://www.w3.org/1999/04/Editing/#3.1>`_,
    each request **must** include an ``ETag`` of the resource it is replacing.
    The ``ETag`` **must** be part of the ``If-Match`` header.

    ``PATCH`` method should be used for partial modification of
    a resource. Each request **should** include an ``ETag`` of the resource
    it is replacing.

**Delete**

    ``DELETE`` method deletes the specified resource.

2.1 Beyond CRUD
~~~~~~~~~~~~~~~

Furthermore, resources **should** also support the following methods:

**Options**

    ``OPTIONS`` method should be used to query for the allowed methods of the
    target resource. The response **must** contain an ``Allow`` header listing
    the allowed methods. This method **may** be combined with the following two
    request headers:

    - ``Access-Control-Request-Headers`` `(more on request headers)
      <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Request-Headers>`_
    - ``Access-Control-Request-Method`` `(more on request methods)
      <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Request-Method>`_

**Head**

    ``HEAD`` method can be used to request the headers that would be returned
    if a given resource were requested using ``GET``. The response to ``HEAD``
    **must not** include a body.

In case you need more verbs or you are not working with a resource, you should
pause since you might be designing a new **communication protocol**. However,
there might be actions which are hard to be expressed through CRUD operations
in a straightforward and comprehensible way. In these cases a pragmatic
approach **can** be followed.

.. _`CRUD`: https://en.wikipedia.org/wiki/Create,_read,_update_and_delete

3. Content Negotiation
----------------------

``Accept``
    All meta-data endpoints should support ``application/json`` and
    optionally they may support ``application/vnd.api+json`` if they
    conform with `JSON API specification`_.


4. Errors
---------

In case of an error, the ``Content-Type`` of the response **must** match the
``Accept`` header of the request. A JSON error response **must** contain an
error object in the response body. The error object **should** contain a unique
error code (that can be looked up for more details), an error message and
possibly a detailed description:

.. code-block:: JSON

    {
        "code": 1234,
        "message": "Something went wrong.",
        "description": "What exactly went wrong."
    }

Furthermore, every error response **must** use a meaningful `HTTP status code
<https://tools.ietf.org/html/rfc7231#section-6.1>`_. The status code **may**
also be part of the error object in the response body.


5. URL structure
----------------

URLs **should** be RESTful in the sense that they represent logical resources
or collections of resources. The plural form should be used as endpoint names.
Whenever possible, a single word should be used to describe resources. Where
compound words cannot be avoided, they are built using **dashes**. For complex
queries (filtering, sorting) query parameters **should** be used.


- URL for the entire collection of contexts:
    ``/contexts``

- URL for a specific context:
    ``/contexts/{id}``


5.1 Relations
~~~~~~~~~~~~~

A relation between resources **must** be represented in the URL structure if
the related resources only exist in the context of the relation. The `github API
<https://developer.github.com/v3/repos/commits/>`_ for example represents commits
always as part of a repository.

- Listing commits on a repository:
    ``GET /repos/{owner}/{repo}/commits``

- Retrieving a single commit:
    ``GET /repos/{owner}/{repo}/commits/{sha}``

If a related resource does exist independently of the related resource,
relations are still represented in the URL structure, however individual
resources are accessed independently.

- URL for all executions related to a given context:
    ``/contexts/{id}/executions``

All relations of a resource **should** be made available following such
patterns.

- ``/projects/{id}/creator`` - single resource can be a ``301`` redirect to the
  resource base URL (e.g. ``Location: /users/1234``).
- ``/projects/{id}/buckets``

In contrast, a specific resource is accessed independently of the relations
which have been followed.

- URL for a specific execution whose id was retrieved trough a context:
  ``/executions/{id}``

To make following relations more convenient, links to the related resources
**should** be included in the response body when a given relation is queried.
In case of a single resource response the links **may** also be included in the
response `link header <https://tools.ietf.org/html/rfc8288#section-3.5>`_.


6. Query Parameters
-------------------

6.1 Filtering
~~~~~~~~~~~~~

Unique query parameters **must** be used for each field that allows filtering.
The list of query parameters that allow filtering **must** be documented for
each API endpoint.

- Retrieving all executions which are currently running:
    ``GET /executions?status=running``


6.2 Sorting
~~~~~~~~~~~

A generic ``sort`` parameter **must** be used to describe sorting rules. If
there are multiple fields that a collection can be sorted by, the ``sort``
parameter **must** accept a list of comma separated fields. The format of the
``sort`` parameter values has to follow: ``field:ASC|DESC``.

- Retrieving all files, ordered alphabetically by file type and by descending
  file size:
  ``GET /files?sort=type:ASC,size:DESC``

6.3 Pagination
~~~~~~~~~~~~~~

Pagination **must** be supported by all endpoints returning more than just
a single resource. Pagination **must** be implemented using the query
parameters ``page`` and ``per_page``. Both the parameters have to accept
any positive integer value. The ``page`` parameter **must** default to 1 
while the default for the ``per_page`` should be set to some value reasonable 
for an endpoint. Non-positive values for both parameters causes 
endpoint to return ``BAD_REQUEST (400)`` response.

Link headers **must** be included in the response indicating:

- first page ``rel="first"``;
- previous page ``rel="prev"`` (present only when the current page is not the first page);
- next page ``rel="next"`` (present only when the current page is not the last page);
- last page ``rel="last"`` (present only when the total number of items is known).

Link headers are described by `RFC 8288
<https://tools.ietf.org/html/rfc8288>`_.

Additional headers **must** be included in the response to present information
about pagination:

- ``Total``	for the total number of items (present only when the total number of items is known);
- ``Total-Pages``	for the total number of pages (present only when the total number of items is known);
- ``Per-Page`` for the number of items per page;
- ``Page`` for the index of the current page (starting at 1);
- ``Prev-Page`` for the index of the previous page (present only when the current page is not the first page);
- ``Next-Page`` for the index of the next page (present only when the current page is not the last page).
