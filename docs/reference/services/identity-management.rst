.. _user_management:

Content
=======

- :ref:`im_user_account_service`
- :ref:`im_admin_console`

**Renku**'s identity management is based on Keycloak. In the following two
paragraphs we document the steps to add a user or modify a users security
settings. For further information, we refer the reader to the `Keycloak
documentation <http://www.keycloak.org/docs/>`_.


.. _im_user_account_service:

User Account Services
---------------------

Users can access their profiles through the Keycloak User Account service at
``http://keycloak.<platform_domain>/auth/realms/Renku/account>``. This service
allows users to manage their account, change their credentials, update their
profiles, and view their login sessions.

.. _im_admin_console:

User Management
---------------

The bulk of the user management administrative tasks are done through the
Keycloak admin console. You can go to the console directly at
``<http://keycloak.<platform_domain>/auth>``.  This service allows the platform
administrator to create new realms, create new users, change user attributes,
impersonate users and configure the security settings of the Keycloak service.
