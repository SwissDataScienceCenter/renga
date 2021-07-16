.. _core_service:

Core service
============

A lot of Renku core functionality is sometimes needed to be accessed via HTTP or executed
in the background. The main purpose of core service is to address those needs.

The following diagram describes components and architecture of the service:


.. _fig-core-service-architecture:

.. graphviz:: /_static/graphviz/core_service_architecture.dot

The resources are segmented by user and can not be shared between them.
They could be files or projects on top of which the user executes subsequent operations.
Each resource within the service has a default time to live after which the resource is evicted.

Sequence diagram of service APIs
""""""""""""""""""""""""""""""""
**GET /<prefix>/cache.files_list**

An endpoint to list all uploaded files for a given user.

.. uml:: ../../_static/uml/core-files-list.uml


**POST /<prefix>/cache.files_upload**

An endpoint that allows file upload and tracks it for each user using the service.

.. uml:: ../../_static/uml/core-files-upload.uml


**POST /<prefix>/cache.project_clone**

An endpoint to clone remote project to service cache. Used as a first step in the
flow for executing operations on top of the cloned project.

.. uml:: ../../_static/uml/core-project-clone.uml


**GET /<prefix>/cache.project_list**

An endpoint to list all projects to the service cache for a given user.

.. uml:: ../../_static/uml/core-project-list.uml


**POST /<prefix>/datasets.add**

An endpoint to add a file to dataset. This command is equivalent to the ``renku dataset add`` command.

The following diagram describes the case when we are adding a file from a local service cache
(e.g. user uploaded files):

.. uml:: ../../_static/uml/core-datasets-add-from-cache.uml

This endpoint also supports adding files to a dataset from an external URL.

.. uml:: ../../_static/uml/core-datasets-add-from-url.uml


**POST /<prefix>/datasets.create**

An endpoint to create a new dataset within a project.
This command is equivalent to the ``renku dataset create`` command.

.. uml:: ../../_static/uml/core-datasets-create.uml


**POST /<prefix>/datasets.edit**

An endpoint for editing dataset metadata. This command is equivalent to the ``renku dataset edit`` command.

.. uml:: ../../_static/uml/core-datasets-edit.uml


**GET /<prefix>/datasets.files_list**

An endpoint to list all dataset files within a given project. This command is equivalent
to the ``renku dataset ls-files`` command.

.. uml:: ../../_static/uml/core-datasets-files-list.uml


**POST /<prefix>/datasets.import**

An endpoint for importing datasets from external providers. This command is equivalent
to the ``renku dataset import`` command.

.. uml:: ../../_static/uml/core-datasets-import.uml


**GET /<prefix>/datasets.list**

An endpoint to list of all datasets within a given project. This command is equivalent
to the ``renku dataset ls`` command.

.. uml:: ../../_static/uml/core-datasets-list.uml


**POST /<prefix>/templates.create_project**

An endpoint for creating projects from an external templates repository. This command
is equivalent to the ``renku init -s`` command.

.. uml:: ../../_static/uml/core-templates-create.uml


**GET /<prefix>/templates.read_manifest**

An endpoint for reading manifest files from external templates repositories. This command
is equivalent to the ``renku init -l`` command.

.. uml:: ../../_static/uml/core-templates-read.uml
